import asyncio
import json
import os

from aioredis import Redis
from common.config import tgbot_config
from common.services import TgBotMessageService
from jinja2 import Template
from loguru import logger
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", 6379)
redis_client = Redis.from_url(f"redis://{redis_host}:{redis_port}/0")
tg_bot_token = tgbot_config["token"]
my_chat_id = tgbot_config["my_chat_id"]
tg_bot = TgBotMessageService(redis_client)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# 获取当前文件所在目录
template_dir = os.path.join(BASE_DIR, "templates")
with open(os.path.join(template_dir, "message.jinja"), "r") as f:
    message_tmpl = f.read()


# 定义处理 /start 命令的异步函数
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if msg is None:
        return
    await msg.reply_text("Hello! I am your bot. Send me a message!")


def shorten_address(s, max_length=16):
    """将长字符串缩短为 '前6个字符.....后5个字符' 的格式"""
    if len(s) <= max_length:
        return s  # 如果字符串长度小于等于最大长度，直接返回原字符串
    else:
        return f"{s[:6]}.....{s[-5:]}"


def extend_data(data: dict):
    transaction_type = data["transaction_type"]
    address = data["address"]
    token_mint = data["token_mint"]
    pre_token_balance = data["pre_token_balance"]
    post_token_balance = data["post_token_balance"]

    token_amount_change = post_token_balance - pre_token_balance
    if pre_token_balance == 0:
        change_rate = 0
    else:
        change_rate = token_amount_change / pre_token_balance
    if transaction_type == "clear":
        transaction_direction = "清仓"
    elif transaction_type == "open":
        transaction_direction = "建仓"
    elif transaction_type == "add":
        transaction_direction = "加仓"
    elif transaction_type == "reduce":
        transaction_direction = "减仓"
    else:
        transaction_direction = "未知"

    data["transaction_direction"] = transaction_direction
    data["smart_money_address"] = address
    data["smart_money_alias"] = shorten_address(address)
    data["token_mint"] = token_mint
    data["change_rate"] = change_rate
    return data


def build_message(data: dict):
    transaction_id = data["transaction_id"]
    address = data["address"]
    token_mint = data["token_mint"]
    pre_token_balance = data["pre_token_balance"]
    post_token_balance = data["post_token_balance"]
    signature = data["signature"]
    token_amount_change = post_token_balance - pre_token_balance
    change_rate = data["change_rate"]
    transaction_direction = data["transaction_direction"]

    tmpl = Template(message_tmpl)
    rendered = tmpl.render(
        transaction_id=transaction_id,
        transaction_direction=transaction_direction,
        smart_money_address=address,
        smart_money_alias=shorten_address(address),
        token_mint=token_mint,
        token_amount=data["token_amount"],
        change_rate=f"{change_rate:.2%}",
        change_icon="📈" if token_amount_change > 0 else "📉",
        before_amount=pre_token_balance,
        after_amount=post_token_balance,
        amount_change=abs(token_amount_change),
        token_amount_change=token_amount_change,
        signature=signature,
    )
    return rendered


async def get_latest_message() -> dict | None:
    message = await tg_bot.pop_message(my_chat_id)
    """
    (b'tgbot:5049063827', b'{"address": "EARFf4ZxBRBuPJc1DyhNwXG5GJNJYSEZHNUJwTSGhzyQ", "token_mint": "Gc2yDSR1rUZ4QuWc4yxQ3y7cvAA2AE2QmrjP3a8mpump", "token_amount": 12.85346999997273, "pre_token_balance": 283068.032564, "post_token_balance": 283055.179094, "transaction_type": "reduce", "transaction_id": "EARFf4ZxBRBuPJc1DyhNwXG5GJNJYSEZHNUJwTSGhzyQ:Gc2yDSR1rUZ4QuWc4yxQ3y7cvAA2AE2QmrjP3a8mpump:12.85346999997273:reduce", "signature": "42GPWM2XNtAdJBmuyX6owbjRK9Ej2MnkqDKP1K4mSaMgeqYnQ8S11T2MmszkHHNSx9ifnXiPCVgSkc44qVZRbotz"}')
    """
    if message is None:
        return
    _, content = message
    try:
        data = json.loads(content.decode("utf-8"))
    except json.JSONDecodeError:
        logger.error(f"Failed to decode message: {content}")
        return
    return data


async def send_message(bot: Bot, chat_id: str, data: dict) -> None:
    address = data["address"]
    token_mint = data["token_mint"]
    data = extend_data(data)
    # change_rate = f"{data['change_rate']:.2%}"
    # tx_direction = data["transaction_direction"]
    text = build_message(data)

    keyboards = [
        [
            InlineKeyboardButton(
                "查看k线",
                url=f"https://gmgn.ai/sol/token/{token_mint}",
            ),
            InlineKeyboardButton(
                "个人持仓",
                url=f"https://gmgn.ai/sol/address/{address}",
            ),
            InlineKeyboardButton(
                "查钱包盈亏",
                url=f"https://t.me/GMGN_smartmoney_bot?start={address}",
            ),
        ],
        [
            InlineKeyboardButton(
                "快速交易",
                url=f"https://t.me/GMGN_sol_bot?start={token_mint}",
            ),
            # InlineKeyboardButton(
            #     f"跟随交易({tx_direction} {change_rate})",
            #     url=f"https://t.me/GMGN_sol_bot?start={token_mint}",
            # ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboards)

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )
    logger.info(f"Sent message to {chat_id}")


async def func(bot):
    while True:
        logger.info("Checking for new messages...")
        data = await get_latest_message()
        if data is None:
            continue
        await send_message(bot, my_chat_id, data)


# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     msg = update.message
#     if msg is None:
#         return
#     logger.info(f"Chat ID: {msg.chat_id}, Message: {msg.text}")
#
#     if msg.reply_markup:
#         for row in msg.reply_markup.inline_keyboard:
#             for button in row:
#                 # 打印按钮的文本和回调数据或 URL
#                 button_text = button.text
#                 if button.url:
#                     button_action = f"URL: {button.url}"
#                 else:
#                     button_action = f"Callback Data: {button.callback_data}"
#                 logger.info(f"Button Text: {button_text}, Action: {button_action}")
#
#     await msg.reply_text(f"You said: {msg.text}")


def main() -> None:
    # application = ApplicationBuilder().token(tg_bot_token).build()
    # bot = application.bot
    #
    # # 注册处理程序
    # # application.add_handler(CommandHandler("start", start))
    # # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    #
    # application.create_task(func(bot))
    # application.run_polling()
    bot = Bot(token=tg_bot_token)
    asyncio.run(func(bot))


if __name__ == "__main__":
    main()
