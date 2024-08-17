import json
import os
import time
from inspect import isawaitable
from typing import Any

import redis
from common.config import tgbot_config
from common.rpc_nodes import choice_rpc_node
from common.services import (
    LatestTransactionDetailsProduerService,
    LatestTransactionSignaturesConsumerService,
    ParserErrorService,
    TgBotMessageService,
)
from loguru import logger
from rich.console import Console
from solana.exceptions import SolanaRpcException
from solana.rpc.api import Client
from solders.signature import Signature

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", 6379)
# 连接到 Solana 主网
pool = redis.ConnectionPool.from_url(f"redis://{redis_host}:{redis_port}")
redis_client = redis.Redis.from_pool(pool)
console = Console()
tg_chat_id = tgbot_config["my_chat_id"]
tg_bot_service = TgBotMessageService(redis_client)
parser_error_service = ParserErrorService(redis_client)
latest_transaction_signatures_consumer_service = (
    LatestTransactionSignaturesConsumerService(
        redis_client,
        group_name="solana:latest_transaction_signatures",
    )
)
latest_transaction_details_service = LatestTransactionDetailsProduerService(
    redis_client
)


# 获取交易详情
def get_transaction_details(signature: Signature) -> dict[str, Any]:
    rpc_api = choice_rpc_node()
    logger.info(f"Using RPC node: {rpc_api}")
    client = Client(f"https://{rpc_api}")
    response = client.get_transaction(
        signature,
        encoding="jsonParsed",
        max_supported_transaction_version=0,
    )
    js_data = response.to_json()
    return json.loads(js_data)["result"]


def get_signer_address(transaction: dict[str, Any]) -> list[str]:
    """获取交易的签名地址"""
    # 签名地址的数量
    signer_count = len(transaction["transaction"]["signatures"])
    if signer_count > 2:
        # 不处理多个签名地址的情况
        raise ValueError("多个签名地址")
    account_keys = transaction["transaction"]["message"]["accountKeys"]

    signer_pubkeys = []
    for key in account_keys:
        if key["signer"] is True:
            signer_pubkeys.append(key["pubkey"])
    return signer_pubkeys


def parse_token_bal_change(transaction_meta: dict[str, Any]) -> dict[str, Any]:
    post_token_balances = transaction_meta["postTokenBalances"]
    pre_token_balances = transaction_meta["preTokenBalances"]

    pre_token_balances_map = {}
    for balance in pre_token_balances:
        mint = balance["mint"]
        owner = balance["owner"]
        pre_token_balances_map[f"{owner}:{mint}"] = balance["uiTokenAmount"]["uiAmount"]

    post_token_balances_map = {}
    for balance in post_token_balances:
        mint = balance["mint"]
        owner = balance["owner"]
        post_token_balances_map[f"{owner}:{mint}"] = balance["uiTokenAmount"][
            "uiAmount"
        ]

    data = {}
    if len(pre_token_balances_map) > len(post_token_balances_map):
        for key, pre_balance in pre_token_balances_map.items():
            owner, mint = key.split(":")
            post_balance = post_token_balances_map.get(key, 0)
            data[owner] = {
                "owner": owner,
                "mint": mint,
                "pre_balance": pre_balance,
                "post_balance": post_balance,
                "change_amount": post_balance - pre_balance,
                "change_type": "inc" if post_balance > pre_balance else "dec",
            }
    else:
        for key, post_balance in post_token_balances_map.items():
            owner, mint = key.split(":")
            pre_balance = pre_token_balances_map.get(key, 0)
            data[owner] = {
                "owner": owner,
                "mint": mint,
                "pre_balance": pre_balance,
                "post_balance": post_balance,
                "change_amount": post_balance - pre_balance,
                "change_type": "inc" if post_balance > pre_balance else "dec",
            }
    return data


def parse_transaction(transaction, buyer_address: str):
    meta = transaction["meta"]
    if not (meta["err"] is None and meta["status"]["Ok"] is None):
        raise ValueError("交易失败")

    token_bal_change = parse_token_bal_change(meta)
    pre_token_balance = token_bal_change[buyer_address]["pre_balance"]
    post_token_balance = token_bal_change[buyer_address]["post_balance"]
    token_mint = token_bal_change[buyer_address]["mint"]
    change_amount = token_bal_change[buyer_address]["change_amount"]

    # 建仓，加仓，减仓，清仓
    if pre_token_balance == 0 and post_token_balance > 0:
        transaction_type = "open"
    elif pre_token_balance > 0 and post_token_balance == 0:
        transaction_type = "clear"
    elif pre_token_balance > 0 and post_token_balance > pre_token_balance:
        transaction_type = "add"
    elif pre_token_balance > 0 and post_token_balance < pre_token_balance:
        transaction_type = "reduce"
    elif pre_token_balance == post_token_balance == 0:
        transaction_type = "invalid"
    else:
        raise ValueError("未知交易类型")

    return {
        "address": buyer_address,
        "token_mint": token_mint,
        "token_amount": post_token_balance,
        "pre_token_balance": pre_token_balance,
        "post_token_balance": post_token_balance,
        "change_amount": change_amount,
        "transaction_type": transaction_type,
    }


def calculate_transaction_id(data: dict[str, Any]) -> str:
    """计算交易 ID"""
    return f"{data['address']}:{data['token_mint']}:{data['token_amount']}:{data['transaction_type']}"


def handle_transaction(transaction_signature: str) -> dict[str, Any] | None:
    sig = Signature.from_string(transaction_signature)
    transaction_details = get_transaction_details(sig)
    if not transaction_details:
        return None

    data = None
    account_keys = get_signer_address(transaction_details)
    for key in account_keys[::-1]:
        data = parse_transaction(transaction_details, key)
        if data["token_mint"] is not None:
            break

    if data is None:
        raise ValueError(f"解析数据为空: {transaction_signature}")

    transaction_id = calculate_transaction_id(data)
    data["transaction_id"] = transaction_id
    data["signature"] = transaction_signature
    return data


def func():
    pending_messages = (
        latest_transaction_signatures_consumer_service.reget_pending_messages()
    )
    if pending_messages:
        messages = pending_messages
        logger.info("从 pending_messages 中获取交易签名")
    else:
        # 从 redis 中获取交易签名
        new_messages = (
            latest_transaction_signatures_consumer_service.get_latest_transaction_signatures()
        )
        _, messages = new_messages[0]  # type: ignore
        logger.info("从 最新交易签名 中获取交易签名")

    assert not isawaitable(messages), "never occurs"
    if not messages:
        logger.warning("没有交易签名")
        return

    message = messages[0]
    _id, payload = message
    transaction_signature = payload[b"signature"].decode("utf-8")
    logger.info(f"获取到交易签名: {transaction_signature}")

    try:
        data = None
        # PERF: 优化请求交易详情
        # 目前使用的 API，并不能在交易的第一时间获取到交易详情
        # 所以只能在这里尝试多次重试，直到获取到交易详情
        for _ in range(60):
            try:
                data = handle_transaction(transaction_signature)
            except SolanaRpcException:
                logger.warning(f"请求交易详情失败: {transaction_signature}")
                continue
            if data:
                break
            logger.warning(
                f"未找到交易结果: {transaction_signature}, 可能是未完成的交易"
            )
            time.sleep(1)
        else:
            raise ValueError("未找到交易结果")

        assert data is not None, "never occurs"
        if data["transaction_type"] == "invalid":
            logger.info(f"无效交易: {transaction_signature} | 放弃处理")
            parser_error_service.add_error(transaction_signature, "无效交易")
            return
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.error(f"处理交易失败: {transaction_signature} | Error: {e}")
        parser_error_service.add_error(transaction_signature, str(e))
    else:
        latest_transaction_details_service.add_transaction_details(data)
        logger.info(f"处理交易成功: {transaction_signature} | {data}")
        tg_bot_service.send_message(tg_chat_id, json.dumps(data))
        show_message(data)
    finally:
        latest_transaction_signatures_consumer_service.ack(_id)
        logger.info(f"ACK: {_id}")


def show_message(data: dict):
    transaction_id = data["transaction_id"]
    transaction_type = data["transaction_type"]
    address = data["address"]
    token_mint = data["token_mint"]
    pre_token_balance = data["pre_token_balance"]
    post_token_balance = data["post_token_balance"]
    signature = data["signature"]

    token_amount_change = post_token_balance - pre_token_balance

    # token 数量变化率
    if pre_token_balance == 0:
        change_rate = 0
    else:
        change_rate = token_amount_change / pre_token_balance

    text = f"""
交易ID: {transaction_id}
签名: https://solscan.io/tx/{signature}
聪明钱地址: {address}
交易类型: {transaction_type}
Token地址: {token_mint}
Token余额: {data["token_amount"]}
Token余额变化率: {change_rate:.2%}
交易前的余额: {data["pre_token_balance"]}
交易后的余额: {data["post_token_balance"]}"""
    console.print(text)


def main():

    while 1:
        try:
            func()
        except Exception as e:
            tg_bot_service.send_message(tg_chat_id, "交易处理失败")
            logger.error(f"处理交易失败: {e}")
        time.sleep(1)


if __name__ == "__main__":
    main()
    # sig = Signature.from_string(
    #     "2BYULzw6cGCXZCezCKwHpboyXsv3DDSGrapvJBikceTuAyssQaqXsVCoWPUMP9TmBGe4vJah4ojRZLr2mmPCsm7v"
    # )
    # data = get_transaction_details(sig)
    # with open("data.json", "w") as f:
    #     f.write(json.dumps(data))
    # data = handle_transaction(
    #     "2BYULzw6cGCXZCezCKwHpboyXsv3DDSGrapvJBikceTuAyssQaqXsVCoWPUMP9TmBGe4vJah4ojRZLr2mmPCsm7v"
    # )
    # print(data)
