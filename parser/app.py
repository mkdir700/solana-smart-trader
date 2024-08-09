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


def get_signer_address(transaction: dict[str, Any]) -> str:
    """获取交易的签名地址"""
    keys = transaction["transaction"]["message"]["accountKeys"]
    for key in keys:
        if key["signer"] is True:
            return key["pubkey"]
    raise ValueError("未找到签名地址")


def parse_transaction(transaction):
    buyer_address = get_signer_address(transaction)
    token_mint = None

    meta = transaction["meta"]

    # 获取交易后的 token 余额
    post_token_balances = meta["postTokenBalances"]
    for balance in post_token_balances:
        if balance["owner"] == buyer_address:
            token_mint = balance["mint"]
            ui_amount = balance["uiTokenAmount"]["uiAmount"]
            # decimals = balance["uiTokenAmount"]["decimals"]
            # post_token_balance = amount / 10**decimals
            if ui_amount is None:
                post_token_balance = 0
            else:
                post_token_balance = ui_amount
            break
    else:
        token_mint = None
        post_token_balance = 0

    # 获取交易前的 token 余额
    pre_token_balances = meta["preTokenBalances"]
    for balance in pre_token_balances:
        if balance["owner"] == buyer_address and balance["mint"] == token_mint:
            ui_amount = balance["uiTokenAmount"]["uiAmount"]
            # decimals = balance["uiTokenAmount"]["decimals"]
            # pre_token_balance = amount / 10**decimals
            if ui_amount is None:
                pre_token_balance = 0
            else:
                pre_token_balance = ui_amount
            break
    else:
        pre_token_balance = 0

    # sol_amount = None
    # 获取本次交换使用了多少 sol
    # instructions = transaction["transaction"]["message"]["instructions"]
    # for instruction in instructions:
    #     if "parsed" not in instruction:
    #         continue
    #     if instruction["program"] != "system":
    #         continue
    #     if instruction["parsed"]["type"] != "transfer":
    #         continue
    #     lamports = instruction["parsed"]["info"]["lamports"]
    #     if instruction["parsed"]["info"]["source"] == buyer_address:
    #         sol_amount = lamports / 10**9
    #         break
    # if sol_amount is None:
    #     raise ValueError("未找到交易使用的 SOL 数量")

    # 本次交易的 token 数量
    token_amount = abs(post_token_balance - pre_token_balance)

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
        "token_amount": token_amount,
        # "sol_amount": sol_amount,
        "pre_token_balance": pre_token_balance,
        "post_token_balance": post_token_balance,
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

    data = parse_transaction(transaction_details)
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
        for _ in range(60):
            # 处理交易
            data = handle_transaction(transaction_signature)
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
            logger.info(f"无效交易: {transaction_signature}, 放弃处理")
            parser_error_service.add_error(transaction_signature, "无效交易")
            return

    except SolanaRpcException:
        logger.error(f"处理交易失败: {transaction_signature}, SolanaRpcException")
        parser_error_service.add_error(transaction_signature, "SolanaRpcException")
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.error(f"处理交易失败: {transaction_signature}, Error: {e}")
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
