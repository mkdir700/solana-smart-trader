from solbot_common.constants import PUMP_FUN_PROGRAM
from solbot_common.log import logger
from solbot_common.utils.utils import (get_async_client,
                                       get_bonding_curve_account)
from solders.pubkey import Pubkey

from .cached import cached


class LaunchCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.client = get_async_client()

    def __repr__(self) -> str:
        return "LaunchCache()"

    @cached(ttl=None, noself=True, skip_cache_func=lambda result: not result)
    async def is_pump_token_graduated(self, mint: str | Pubkey) -> bool:
        """Examine if a Pump.fun token has graduated.

        By checking if the token has completed the bonding curve.

        Only cache the result upon graduation.

        Args:
            mint (str): 代币的 mint 地址

        Returns:
            bool: Whether the token has completed the bonding curve

        Raises:
            BondingCurveNotFound: If cannot find the bonding curve account
        """
        result = await get_bonding_curve_account(
            self.client,
            Pubkey.from_string(mint) if isinstance(mint, str) else mint,
            PUMP_FUN_PROGRAM,
        )
        _, _, bonding_curve_account = result
        logger.debug(f"Bonding curve account: {bonding_curve_account}")
        return bonding_curve_account.complete
