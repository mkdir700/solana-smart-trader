import pytest
from common.config import tgbot_config
from telegram.ext import ApplicationBuilder

from app import build_message, send_message

data = {
    "address": "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
    "token_mint": "CN6YBfSnmmSfr2yX6gTg6hyQDo5yx1D2QFMGRxMGpump",
    "token_amount": 33323048.571363,
    "sol_amount": 0.01,
    "pre_token_balance": 33323048.571363,
    "post_token_balance": 0,
    "transaction_type": "clear",
    "transaction_id": "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj:CN6YBfSnmmSfr2yX6gTg6hyQDo5yx1D2QFMGRxMGpump:0.01:33323048.571363:clear",
    "signature": "5DPR8NY9icwPjJkY5a4yH9MaNhdZqvvLqfWFRuwBfwaFM7XVFnepZiKWJaYjoDLQFT4xRHXg87Sgrz8NbfheWxc1",
}


class TestTgBot:
    @pytest.mark.asyncio
    async def test_send_message(self):
        chat_id = tgbot_config["my_chat_id"]
        tg_bot_token = tgbot_config["token"]
        application = ApplicationBuilder().token(tg_bot_token).build()
        await send_message(application.bot, chat_id, data)

    def test_build_message(self):
        text = build_message(data)
        print(text)
