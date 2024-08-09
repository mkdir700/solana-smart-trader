import httpx
import asyncio
from loguru import logger
from telethon import TelegramClient

from .parse import extract_contract_address, extract_top_10_percent, is_safe


class NewPairStrategy:
    def __init__(self, tg_client: TelegramClient, event, bot_id, *, ca: str | None = None) -> None:
        self.tg_client = tg_client
        self.bot_id = bot_id
        self.event = event
        self.raw_message = event.message.message
        if ca:
            self.contract_address = ca
        else:
            self.contract_address = extract_contract_address(self.raw_message)
        if not self.contract_address:
            raise ValueError("No contract address found in the message")

        self.take_profit_percent = 0.3
        self.stop_loss_percent = 0.3
        self.buy_amount = 0.1  # 0.1 SOL

    async def execute(self):
        """执行策略"""
        if not await self._default_buy_condition():
            logger.info(f"{self.contract_address} | 未通过默认买入条件")
            return
        if not await self.buy_condition():
            logger.info(f"{self.contract_address} | 未满足买入条件")
            return
        await self.create_buy_market_order()

    async def _default_buy_condition(self) -> bool:
        """默认买入条件"""
        if not is_safe(self.raw_message):
            logger.info(f"{self.contract_address} | 未通过安全检查")
            return False
        return True

    async def buy_condition(self) -> bool:
        """买入条件"""
        try:
            p = extract_top_10_percent(self.raw_message)
        except Exception as e:
            logger.error(f"提取前10持仓失败: {e}")
            return False
        if p > 0.25:
            logger.info(f"{self.contract_address} | 前10持仓大于 25%")
            return False
        return True

    async def get_buy_price(self) -> float:
        """获取买入价格"""
        # FIXME: pump 内盘价格，当前无法获取
        client = httpx.AsyncClient()
        response = await client.get(
            f"https://price.jup.ag/v4/price?ids={self.contract_address}"
        )
        try:
            price = response.json()["data"][self.contract_address]["price"]
        except Exception as e:
            logger.error(f"获取价格失败: {e}, response: {response.text}")
            raise e
        return price

    async def create_buy_market_order(self):
        """创建市价买入挂单
        /buy ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82 0.5
        表示立即买入 0.5 SOL BOME代币
        """
        try:
            await self.get_buy_price()
        except Exception as e:
            logger.error(f"{self.contract_address} | 获取买入价格失败: {e}")
            return
        buy_command = f"/buy {self.contract_address} {self.buy_amount}"
        await self.tg_client.send_message(self.bot_id, buy_command)
        logger.info(f"{self.contract_address} | Buy | {self.buy_amount} SOL")

    async def callback_buy_success(self):
        """买入成功回调"""
        await self.create_sell_limit_order()

    async def create_sell_limit_order(self):
        """
        创建限价卖出挂单
        /create limitsell ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82 50@0.1 -exp 3600
        表示创建BOME代币限价卖单，卖出50%持仓，触发价 $0.1，过期时间1小时(3600秒)
        """
        try:
            buy_price = await self.get_buy_price()
        except Exception as e:
            logger.error(f"{self.contract_address} | 获取买入价格失败: {e}")
            return
        # 止盈价格 = 买入价格 * 1.3
        # 止损价格 = 买入价格 * 0.7
        take_profit_price = buy_price * (1 + self.take_profit_percent)
        stop_loss_price = buy_price * (1 - self.stop_loss_percent)

        take_profit_command = f"/create limitsell {self.contract_address} 90@{take_profit_price} -exp 3600"
        stop_loss_command = (
            f"/create limitsell {self.contract_address} 100@{stop_loss_price} -exp 3600"
        )
        # 向 bot 发送命令
        await self.tg_client.send_message(self.bot_id, take_profit_command)
        logger.info(f"{self.contract_address} | 创建止盈单 | {take_profit_price}")
        await asyncio.sleep(5)
        await self.tg_client.send_message(self.bot_id, stop_loss_command)
        logger.info(f"{self.contract_address} | 创建止损单 | {stop_loss_price}")
