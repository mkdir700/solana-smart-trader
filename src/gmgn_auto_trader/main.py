import os

from dotenv import load_dotenv
from loguru import logger
from telethon.sync import TelegramClient, events

load_dotenv()
api_id = int(os.environ["tg_api_id"])
api_hash = os.environ["tg_api_hash"]
gmgn_bot_name = os.environ["gmgn_bot_name"]

client = TelegramClient("name", api_id, api_hash)

TmpMap = {}


async def main():
    # 测试向 bot 发送一条消息
    await client.send_message(gmgn_bot_name, "Hello to myself!")


# @client.on(events.NewMessage(pattern="(?i).*Featured New Pair"))
async def hanlde_new_pair(event):
    from gmgn_auto_trader.strategy import NewPairStrategy

    logger.debug("Received new pair message: \n%s", event.message.message)
    obj = NewPairStrategy(client, event, gmgn_bot_name)
    TmpMap[obj.contract_address] = obj
    await obj.execute()


@client.on(events.NewMessage(pattern=r"(?i).*✅ Success\s*\| Cost"))
async def handle_buy_success(event):
    from gmgn_auto_trader.strategy import NewPairStrategy

    ca = event.message.message.rsplit("\n")[-1].strip()
    # if ca in TmpMap:
    #     obj = TmpMap.pop(ca)
    #     await obj.callback_buy_success()
    obj = NewPairStrategy(client, event, gmgn_bot_name, ca=ca)
    await obj.callback_buy_success()


def is_buy_success(raw_message: str) -> bool:
    """
    🎉 BAPE\n🚀 起飞 -4.98%\n💎 持仓 0.019 SOL\n💸 总买入 0.02 SOL\n💰 总卖出 0 SOL\n⏱️ 持有时长 0s \n\n✅ 交易成功\n| 买入 0.02 SOL\n| 收到 3,847.39 BAPE\n| 点击查看最新成交\n\n📊 监控\n| 当前价格 $0.00078\n| 当前市值 $77.2K\n| 钱包余额 0.5015 SOL\n\n分 享邀请链接 点击交易 BAPE (长按复制)\n88VLN88kNGHnrpqwtrhckM9mgN7ZmWHNtVsg22gyrBtK'
    """
    return "✅ 交易成功\n| 买入" in raw_message


@client.on(events.NewMessage(pattern=is_buy_success))
async def handle_buy_success2(event):
    from gmgn_auto_trader.strategy import NewPairStrategy

    logger.debug("Received new pair message: \n%s", event.message.message)
    ca = event.message.message.rsplit("\n")[-1].strip()
    # if ca in TmpMap:
    #     obj = TmpMap.pop(ca)
    #     await obj.callback_buy_success()
    obj = NewPairStrategy(client, event, gmgn_bot_name, ca=ca)
    await obj.callback_buy_success()


# @client.on(events.NewMessage(pattern="(?i).*✅Burnt"))
# async def handle_sell_success(event): ...


# @client.on(events.NewMessage(pattern="(?i).*满 💊💊💊"))
# async def handle_pump_completed(event):
#     from gmgn_auto_trader.strategy import PumpCompletedStrategy
#
#     await PumpCompletedStrategy(client, event, gmgn_bot_name).execute()


# 处理机器人卖出失败的消息
# @client.on(events.NewMessage(pattern="(?i).*sell failed"))
# async def hanlde_sell_failed(event):
# 🏷 Sell Limit Order Triggered
#
# · Sell: 111.6K ballooncat
# · Trigger Price: $0.0{4}85192
# · FDV: $85.2K
#
# ❌sell failed...View on Solscan
# To increase success rate, tap /set to set more tip and trade again.

with client:
    client.run_until_disconnected()
    # client.loop.run_until_complete(main())
