""" Test TradingExecutor class. This uses actual RPC client (and connects to the network)"""

import pytest


@pytest.mark.asyncio
async def test_exec(executor, swap_event_from_logs_second):
    sig = await executor.exec(swap_event_from_logs_second)
    assert sig is not None

