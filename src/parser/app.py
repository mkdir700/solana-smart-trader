import json
import os
import time
from inspect import isawaitable

import redis
from common.config import tgbot_config
from common.services import (
    LatestTransactionDetailsProduerService,
    LatestTransactionSignaturesConsumerService,
    ParserErrorService,
    TgBotMessageService,
)
from loguru import logger

from parsers import TransactionParserWithSolscan

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", 6379)
# 连接到 Solana 主网
pool = redis.ConnectionPool.from_url(f"redis://{redis_host}:{redis_port}")
redis_client = redis.Redis.from_pool(pool)
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


def fetch_latest_transaction_signature() -> tuple | None:
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
        return

    message = messages[0]
    _id, payload = message
    transaction_signature = payload[b"signature"].decode("utf-8")
    return _id, transaction_signature


def process_latest_transaction():
    message = fetch_latest_transaction_signature()
    if message is None:
        logger.warning("无交易签名")
        return

    _id, signature = message
    _id: bytes
    logger.info(f"获取到交易签名: {signature}")

    try:
        tp = TransactionParserWithSolscan(signature)
        if not tp.is_valid():
            logger.warning(f"失败交易: {signature}")
            return

        data = tp.get_result()
        timestamp = _id.decode("utf-8").split("-")[0]
        data["timestamp"] = timestamp
        latest_transaction_details_service.add_transaction_details(data)
        logger.info(f"处理交易成功: {signature} | {data}")
        tg_bot_service.send_message(tg_chat_id, json.dumps(data))
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.error(f"处理交易失败: {signature} | Error: {e}")
        parser_error_service.add_error(signature, str(e))
    finally:
        latest_transaction_signatures_consumer_service.ack(_id)
        logger.info(f"ACK: {_id}")


def run_transaction_processing_loop():
    while 1:
        try:
            process_latest_transaction()
        except Exception as e:
            tg_bot_service.send_message(tg_chat_id, "交易处理失败")
            logger.error(f"处理交易失败: {e}")


if __name__ == "__main__":
    run_transaction_processing_loop()
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
