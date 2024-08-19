import json

from loguru import logger
from redis.client import Redis


class LatestTransactionSignaturesProducerService:

    def __init__(self, redis_client: Redis) -> None:
        self.r = redis_client
        self.stream_key = "solana:latest_transaction_signatures"

    async def add_transaction_signature(self, signature: str):
        await self.r.xadd(
            "solana:latest_transaction_signatures",
            {"signature": signature},
            maxlen=1000,
        )


class LatestTransactionSignaturesConsumerService:

    def __init__(self, redis_client: Redis, group_name: str) -> None:
        self.r = redis_client
        self.stream_key = "solana:latest_transaction_signatures"
        self.group_name = group_name
        try:
            self.create_consumer_group()
        except Exception:
            pass

    def create_consumer_group(self):
        self.r.xgroup_create(
            name=self.stream_key,
            groupname=self.group_name,
            id="0",
            mkstream=True,
        )

    def reget_pending_messages(self) -> list:
        messages = self.r.xpending(self.stream_key, self.group_name)
        min_ = messages.get("min")
        max_ = messages.get("max")

        if min_ is None or max_ is None:
            return

        logger.info(f"min: {min_}, max: {max_}")
        pending_messages = self.r.xrange(self.stream_key, min=min_, max=max_)
        return pending_messages

    def get_latest_transaction_signatures(self):
        messages = self.r.xreadgroup(
            groupname=self.group_name,
            consumername=self.group_name,
            streams={self.stream_key: ">"},
            count=1,
            block=0,
        )
        return messages

    def ack(self, message_id):
        self.r.xack(
            self.stream_key,
            self.group_name,
            message_id,
        )

    def trim(self, maxlen: int = 10):
        self.r.xtrim(self.stream_key, maxlen=maxlen)


class LatestTransactionDetailsProduerService:

    def __init__(self, redis_client: Redis) -> None:
        self.r = redis_client
        self.stream_key = "solana:latest_transaction_details"

    def add_transaction_details(self, data: dict):
        self.r.xadd(
            self.stream_key,
            {"payload": json.dumps(data)},
            maxlen=1000,
        )

    def ack(self, message_id):
        self.r.xack(
            "solana:latest_transaction_signatures",
            "solana:latest_transaction_signatures",
            message_id,
        )


class TgBotMessageService:

    def __init__(self, redis_client) -> None:
        self.r = redis_client

    def send_message(self, chat_id: str, message: str):
        self.r.rpush(f"tgbot:{chat_id}", message)

    async def pop_message(self, chat_id: str, timeout: int = 0) -> dict | None:
        message = await self.r.blpop(f"tgbot:{chat_id}", timeout=timeout)
        """(b'tgbot:5049063827', b'{"owner": "FJWj7EMzyT859Ad5CfTERSNKjmEWTyyY1EYunpUetiZk", "signature": "5Nc7dRpG4bogZaPySj47enfaEBjK8fAJjUzx4sMGQp9wW1frcLUVrVqCEUST49uB9nMhyUMBVhPsWySguwqX9hWs", "transaction_id": "FJWj7EMzyT859Ad5CfTERSNKjmEWTyyY1EYunpUetiZk:A2qGKaCWQqjFyT1jsssNPnysfYdZhALRJxuRYsq3pump:31768200.0:open", "transaction_type": "open", "token": {"mint": "A2qGKaCWQqjFyT1jsssNPnysfYdZhALRJxuRYsq3pump", "amount": 31768200.0, "pre_balance": 0.0, "post_balance": 31768200.0, "change_amount": 31768200.0, "name": "SPL Token", "symbol": "SPL"}, "sol": {"pre_balance": 16.324299576, "post_balance": 15.382390187, "change_amount": -0.941909389}, "platform": "Pump", "timestamp": "1724052400539"}')"""
        if not message:
            return None
        try:
            return json.loads(message[1].decode("utf-8"))
        except json.JSONDecodeError:
            logger.error(f"Failed to decode message, message: {message}")
            return None


class ParserErrorService:
    """解析错误服务

    用于记录解析交易时的错误
    """

    def __init__(self, redis_client: Redis) -> None:
        self.r = redis_client
        self.stream_key = "solana:parser_error"

    def add_error(self, transaction_signature: str, error: str):
        """添加错误信息到 stream 中"""
        self.r.xadd(
            self.stream_key,
            {"transaction_signature": transaction_signature, "error": error},
        )

    def get_errors(self, count: int = 1):
        """获取错误信息"""
        return self.r.xrange(self.stream_key, count=count)
