import asyncio
import json
import os

import redis.asyncio as redis
from common.config import monitor_config
from common.rpc_nodes import choice_rpc_node
from loguru import logger
from solana.rpc.commitment import Processed
from solana.rpc.websocket_api import connect
from solders.pubkey import Pubkey
from solders.rpc.config import RpcTransactionLogsFilterMentions

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", 6379)
# 连接到 Solana 主网
pool = redis.ConnectionPool.from_url(f"redis://{redis_host}:{redis_port}")
client = redis.Redis.from_pool(pool)
ping_resp = client.ping()


async def main():
    addresses = monitor_config.get("smart_wallets")
    if not addresses:
        raise ValueError("No smart wallets found in config.toml")
    addresses = set(addresses)

    rpc_api = choice_rpc_node()
    logger.info(f"Using RPC node: {rpc_api}")
    async with connect(f"wss://{rpc_api}") as websocket:
        logger.info(f"Listening for changes on accounts: {addresses}")

        # 订阅多个账户
        for address in addresses:
            pubkey = Pubkey.from_string(address)
            await websocket.logs_subscribe(
                filter_=RpcTransactionLogsFilterMentions(pubkey),
                commitment=Processed,
            )

        while True:
            messages = await websocket.recv()
            for message in messages:
                text = message.to_json()
                js = json.loads(text)
                result = js.get("result")

                if not isinstance(result, dict):
                    continue

                try:
                    signature = result["value"]["signature"]
                except KeyError:
                    print(js)
                    continue

                # 保存到 redis
                await client.xadd(
                    "solana:latest_transaction_signatures",
                    {"signature": signature},
                    maxlen=1000,
                )
                logger.info(
                    f"Transaction detected: {signature}, details: https://solscan.io/tx/{signature}"
                )


if __name__ == "__main__":
    asyncio.run(main())
