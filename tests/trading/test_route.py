"""Tests for the trading route finding logic. This uses actual RPC client (and connects to the network)"""


import pytest
from solbot_common.constants import PUMP_FUN_PROGRAM

from app.trading.trading.transaction import TradingRoute

PUMP_FUN_PROGRAM_ID = str(PUMP_FUN_PROGRAM)
#RAY_V4_PROGRAM_ID = str(RAY_V4)

@pytest.mark.asyncio
@pytest.mark.parametrize("swap_event_fixture,expected_route", [
    ("swap_event_from_logs", TradingRoute.PUMP),
    ("swap_event_from_logs_second", TradingRoute.PUMP),
    ("swap_event_from_logs_third", TradingRoute.DEX),
    ("swap_event_from_logs_fourth", TradingRoute.PUMP),
    ("swap_event_from_logs_fifth", TradingRoute.DEX),
])
async def test_find_route(executor, request, swap_event_fixture, expected_route):
    """Test the find_trading_route method with both log examples"""
    swap_event = request.getfixturevalue(swap_event_fixture)
    route = await executor.find_route(swap_event)
    assert route == expected_route
 