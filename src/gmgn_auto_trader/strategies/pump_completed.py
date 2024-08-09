from loguru import logger

from gmgn_auto_trader.parse import is_dev_rich


class PumpCompletedStrategy(NewPairStrategy):
    # 是否在5分钟内完成了pump
    async def buy_condition(self) -> bool:
        if not is_dev_rich(self.raw_message):
            logger.info(f"{self.contract_address} | 开发者不是很有钱")
            return False
        return True
