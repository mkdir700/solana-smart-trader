import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from trading.swap import SwapDirection
from trading.transaction import AggregateTransactionBuilder, TradingService
from trading.transaction.builders.base import TransactionBuilder
from trading.transaction.builders.pump import PumpTransactionBuilder
from trading.transaction.builders.ray_v4 import RaydiumV4TransactionBuilder
from trading.transaction.protocol import TradingRoute


@pytest.fixture
def mock_rpc_client():
    return AsyncMock(spec=AsyncClient)


@pytest.fixture
def mock_transaction():
    return MagicMock(spec=VersionedTransaction)


@pytest.fixture
def mock_keypair():
    return MagicMock(spec=Keypair)


class MockBuilder(TransactionBuilder):
    """用于测试的模拟构建器"""

    def __init__(self, rpc_client: AsyncClient, delay: float = 0, should_fail: bool = False):
        super().__init__(rpc_client)
        self.delay = delay
        self.should_fail = should_fail
        self.build_called = False

    async def build_swap_transaction(self, *args, **kwargs):
        self.build_called = True
        await asyncio.sleep(self.delay)
        if self.should_fail:
            raise Exception("Mock builder failed")
        return MagicMock(spec=VersionedTransaction)


@pytest.mark.asyncio
async def test_aggregate_builder_returns_fastest_success():
    """Testing the aggregation builder returns the fastest successful results"""
    mock_client = AsyncMock(spec=AsyncClient)

    # Create three mock builders with different delays
    fast_builder = MockBuilder(mock_client, delay=0.1)
    slow_builder = MockBuilder(mock_client, delay=0.3)
    failing_builder = MockBuilder(mock_client, delay=0.2, should_fail=True)

    aggregate_builder = AggregateTransactionBuilder(
        mock_client, [fast_builder, slow_builder, failing_builder]
    )

    # Execute the build
    result = await aggregate_builder.build_swap_transaction(
        keypair=MagicMock(),
        token_address="mock_token",
        ui_amount=1.0,
        swap_direction=SwapDirection.Buy,
        slippage_bps=100,
    )

    # Verify the result
    assert isinstance(result, VersionedTransaction)
    assert fast_builder.build_called
    assert slow_builder.build_called
    assert failing_builder.build_called


@pytest.mark.asyncio
async def test_aggregate_builder_handles_all_failures():
    """测试聚合构建器处理所有构建器失败的情况"""
    mock_client = AsyncMock(spec=AsyncClient)

    # 创建两个会失败的构建器
    failing_builder1 = MockBuilder(mock_client, should_fail=True)
    failing_builder2 = MockBuilder(mock_client, should_fail=True)

    aggregate_builder = AggregateTransactionBuilder(
        mock_client, [failing_builder1, failing_builder2]
    )

    # 验证异常抛出
    with pytest.raises(Exception) as exc_info:
        await aggregate_builder.build_swap_transaction(
            keypair=MagicMock(),
            token_address="mock_token",
            ui_amount=1.0,
            swap_direction=SwapDirection.Buy,
            slippage_bps=100,
        )

    assert str(exc_info.value) == "All transaction builders failed"
    assert failing_builder1.build_called
    assert failing_builder2.build_called


@pytest.mark.asyncio
async def test_trading_service_route_selection():
    """测试交易服务的路由选择功能"""
    mock_client = AsyncMock(spec=AsyncClient)
    service = TradingService(mock_client)

    # 测试 PUMP 路由
    builder = service.select_builder(TradingRoute.PUMP)
    assert isinstance(builder, PumpTransactionBuilder)

    # 测试 RAYDIUM_V4 路由
    builder = service.select_builder(TradingRoute.RAYDIUM_V4)
    assert isinstance(builder, RaydiumV4TransactionBuilder)

    # 测试无效路由
    with pytest.raises(ValueError) as exc_info:
        service.select_builder("INVALID_ROUTE")  # type: ignore[invalid-argument-type]
    assert "Unsupported trading route" in str(exc_info.value)


@pytest.mark.asyncio
async def test_trading_service_use_route():
    """测试交易服务的路由使用功能"""
    mock_client = AsyncMock(spec=AsyncClient)

    with (
        patch("trading.transaction.factory.GMGNTransactionSender") as mock_gmgn_sender,
        patch("trading.transaction.factory.JitoTransactionSender") as mock_jito_sender,
        patch("trading.transaction.factory.DefaultTransactionSender") as mock_default_sender,
    ):
        service = TradingService(mock_client)

        # 测试 GMGN 路由
        # NOTE: GMGN is not an enumerated trading route
        # swapper = service.use_route(TradingRoute.GMGN)
        # assert isinstance(swapper.builder, GMGNTransactionBuilder)
        # mock_gmgn_sender.assert_called_once()

        # 测试带 Jito 的普通路由
        swapper = service.use_route(TradingRoute.PUMP, use_jito=True)
        assert isinstance(swapper.builder, PumpTransactionBuilder)
        mock_jito_sender.assert_called_once()

        # 测试默认路由
        swapper = service.use_route(TradingRoute.RAYDIUM_V4)
        assert isinstance(swapper.builder, RaydiumV4TransactionBuilder)
        mock_default_sender.assert_called_once()

        # DEX
        swapper = service.use_route(TradingRoute.DEX)
        assert isinstance(swapper.builder, AggregateTransactionBuilder)
        mock_default_sender.assert_called_once()
