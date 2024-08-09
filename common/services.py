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

    def add_transaction_details(self, data):
        self.r.xadd(
            self.stream_key,
            {**data},
            maxlen=1000,
        )

    def ack(self, message_id):
        self.r.xack(
            "solana:latest_transaction_signatures",
            "solana:latest_transaction_signatures",
            message_id,
        )


class TgBotMessageService:

    def __init__(self, redis_client: Redis) -> None:
        self.r = redis_client
        self.prefix = "tgbot"

    def send_message(self, chat_id: str, message: str):
        self.r.rpush(f"{self.prefix}:{chat_id}", message)

    async def pop_message(self, chat_id: str):
        return await self.r.lpop(f"{self.prefix}:{chat_id}")


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
