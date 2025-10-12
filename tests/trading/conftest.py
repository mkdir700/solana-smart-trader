import pytest
import pytest_asyncio
from solbot_common.types.swap import SwapEvent
from solbot_common.types.tx import TxEvent, TxType
from solbot_common.utils import get_async_client


@pytest_asyncio.fixture
async def rpc_client():
    """Real Async Solana RPC client shared across trading tests."""
    client = get_async_client()
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture
def executor(rpc_client):
    """Provide a TradingExecutor with external calls stubbed for determinism."""
    import app.trading.trading.executor as executor_module
    from app.trading.trading.executor import TradingExecutor

    trading_executor = TradingExecutor(rpc_client)

    return trading_executor

#SwapEvent:
#user_pubkey='5b9tuvErmHAXpfGNv4wyRDQx6mLhYp4tKry52gxhToBa' swap_mode='ExactIn' input_mint='So1111111111111111111111111111
#1111111111112' output_mint='8qAbzjWBxD2kxnNwE9voR9Xkr2zT8mg1aM6ri34Jpump' amount=50000000 ui_amount=0.05 timestamp=1756448961 amount_pct=None swap_in_type='qty' priority_fee=0.0001 slippage_bps=250 by='copytrade' dynamic_slippage=False min_sl
#ippage_bps=None max_slippage_bps=None program_id='6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P' tx_event=TxEvent(signature='53XTg3825Q46PVDeJ6qVoP7nHx3RxKwhNNarYGKgfbD8V4FTPyztxCXDsXU3pBPdcztn9PqgxfJg6cJgEBPZEQEB', from_amount=340004999, from_
#decimals=9, to_amount=4181819987502, to_decimals=6, mint='8qAbzjWBxD2kxnNwE9voR9Xkr2zT8mg1aM6ri34Jpump', who='DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj', tx_type=<TxType.ADD_POSITION: 'add_position'>, tx_direction='buy', timestamp=17564489
#61, pre_token_amount=25274744460671, post_token_amount=29456564448173, program_id='6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P')

#SwapEvent #2
#user_pubkey='5b9tuvErmHAXpfGNv4wyRDQx6mLhYp4tKry52gxhToBa' swap_mode='ExactIn' input_mint='So1111111111111111111111111111
#1111111111112' output_mint='6NqXBdXA38ZXEGU7nGfp9Fr4JSTKgtfZDqZit91Dbonk' amount=50000000 ui_amount=0.05 timestamp=1756531032 amount_pct=None swap_in_type='qty' priority_fee=0.0001 slippage_bps=250 by='copytrade' dynamic_slippage=False min_sl
#ippage_bps=None max_slippage_bps=None program_id=None tx_event=TxEvent(signature='3gqWLDzno5LKU1asduxDdACMbQmQFdvfwU6WJarnWT3Mcrwb73oYbmfaFaDVLFtyZhwToWi4WZEawL9y9JzdP1RA', from_amount=1090005000, from_decimals=9, to_amount=1037510604527, to_
#decimals=6, mint='6NqXBdXA38ZXEGU7nGfp9Fr4JSTKgtfZDqZit91Dbonk', who='DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj', tx_type=<TxType.ADD_POSITION: 'add_position'>, tx_direction='buy', timestamp=1756531032, pre_token_amount=19836071332282, pos
#t_token_amount=20873581936809, program_id=None)

#SwapEvent #3
#user_pubkey='5b9tuvErmHAXpfGNv4wyRDQx6mLhYp4tKry52gxhToBa' swap_mode='ExactIn' input_mint='So11111111111111111111111111111111111111112' output_mint='7i
#CcjyC8NWooMmpjwaAuFPG7ZeGvSwDjKRMPcNdei3ve' amount=50000000 ui_amount=0.05 timestamp=1756687287 amount_pct=None swap_in_type='qty' priority_fee=0.0001 slippage_bps=250 by='copytrade' dynamic_slippage=False min_slippage_bps=None max_slippage_bps=None program_id='cpamdpZCGK
#Uy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG' tx_event=TxEvent(signature='4CL5kwExbe7JkFFjmGvTqdrpKhV8kjWkpZKy7ovR2GWU2dFBMJEXaBAfVBApzgAxNVKbSaNzuk7SZjnQbvwSyfZf', from_amount=5092044280, from_decimals=9, to_amount=8883051365766, to_decimals=6, mint='7iCcjyC8NWooMmpjwaAuFPG7ZeGvSwD
#jKRMPcNdei3ve', who='DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj', tx_type=<TxType.OPEN_POSITION: 'open_position'>, tx_direction='buy', timestamp=1756687287, pre_token_amount=0, post_token_amount=8883051365766, program_id='cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG')

#SwapEvent #4
#user_pubkey='5b9tuvErmHAXpfGNv4wyRDQx6mLhYp4tKry52gxhToBa' swap_mode='ExactIn' input_mint='So11111111111111111111111111111111111111112' output_mint='6n
#AvJcCLUJKffEXDRZ4SzgHcssgZJYxJ6j5xbj4qpump' amount=50000000 ui_amount=0.05 timestamp=1757642156 amount_pct=None swap_in_type='qty' priority_fee=0.002 slippage_bps=3000 by='copytrade' dynamic_slippage=False min_slippage_bps=None max_slippage_bps=None program_id='6EF8rrecth
#R5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P' tx_event=TxEvent(signature='37URoS3xVL5BYgH7SYb7AdQz5gzAPph366ZKFP779CeiQRKbbzZnuYm1MgFaJ1ZmbPSWxLoo36USSr4hY8QSZWpX', from_amount=1424953722, from_decimals=9, to_amount=42923062985000, to_decimals=6, mint='6nAvJcCLUJKffEXDRZ4SzgHcssgZJY
#xJ6j5xbj4qpump', who='suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', tx_type=<TxType.OPEN_POSITION: 'open_position'>, tx_direction='buy', timestamp=1757642156, pre_token_amount=0, post_token_amount=42923062985000, program_id='6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P')


#SwapEvent #5
#user_pubkey='5b9tuvErmHAXpfGNv4wyRDQx6mLhYp4tKry52gxhToBa' swap_mode='ExactIn' input_mint='So11111111111111111111111111111111111111112' output_mint='Co
#novv7mKcmj1UnPSccVoUVqPZMZqXDATJ1JGY7oEj2j' amount=50000000 ui_amount=0.05 timestamp=1757651257 amount_pct=None swap_in_type='qty' priority_fee=0.002 slippage_bps=250 by='copytrade' dynamic_slippage=False min_slippage_bps=None max_slippage_bps=None program_id='6EF8rrecthR
#5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P' tx_event=TxEvent(signature='3AA8G5B5KQa2MBHbPYcWNwzK76gdAVb2De5ooiXtKA6y2jSkFjApNHQMGoRfsHX7btrZ1g82FjxQa9nFqpcMVzN8', from_amount=95827897, from_decimals=9, to_amount=679708083051, to_decimals=6, mint='Conovv7mKcmj1UnPSccVoUVqPZMZqXDATJ1
#JGY7oEj2j', who='suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', tx_type=<TxType.ADD_POSITION: 'add_position'>, tx_direction='buy', timestamp=1757651257, pre_token_amount=30666413513140, post_token_amount=31346121596191, program_id='6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF
#6P')
@pytest.fixture
def tx_event_from_logs() -> TxEvent:
    """TxEvent instance based on logged output."""
    return TxEvent(
        signature="53XTg3825Q46PVDeJ6qVoP7nHx3RxKwhNNarYGKgfbD8V4FTPyztxCXDsXU3pBPdcztn9PqgxfJg6cJgEBPZEQEB",
        from_amount=340004999,
        from_decimals=9,
        to_amount=4181819987502,
        to_decimals=6,
        mint="8qAbzjWBxD2kxnNwE9voR9Xkr2zT8mg1aM6ri34Jpump",
        who="DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        tx_type=TxType.ADD_POSITION,
        tx_direction="buy",
        timestamp=1756448961,
        pre_token_amount=25274744460671,
        post_token_amount=29456564448173,
        program_id="6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
    )


@pytest.fixture
def swap_event_from_logs(tx_event_from_logs) -> SwapEvent:
    """Pump-style swap event resembling on-chain logs.

    Kept minimal to satisfy route selection.
    """
    return SwapEvent(
        user_pubkey="5b9tuvErmHAXpfGNv4wyRDQx6mLhYp4tKry52gxhToBa",
        swap_mode="ExactIn",
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="8qAbzjWBxD2kxnNwE9voR9Xkr2zT8mg1aM6ri34Jpump",
        amount=50000000,
        ui_amount=0.05,
        timestamp=1756448961,
        amount_pct=None,
        swap_in_type="qty",
        priority_fee=0.0001,
        slippage_bps=250,
        by="copytrade",
        dynamic_slippage=False,
        min_slippage_bps=None,
        max_slippage_bps=None,
        program_id="6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
        tx_event=tx_event_from_logs,
    )


@pytest.fixture
def tx_event_from_logs_second() -> TxEvent:
    """Second TxEvent instance derived from logged example (#2)."""
    return TxEvent(
        signature="3gqWLDzno5LKU1asduxDdACMbQmQFdvfwU6WJarnWT3Mcrwb73oYbmfaFaDVLFtyZhwToWi4WZEawL9y9JzdP1RA",
        from_amount=1090005000,
        from_decimals=9,
        to_amount=1037510604527,
        to_decimals=6,
        mint="6NqXBdXA38ZXEGU7nGfp9Fr4JSTKgtfZDqZit91Dbonk",
        who="DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        tx_type=TxType.ADD_POSITION,
        tx_direction="buy",
        timestamp=1756531032,
        pre_token_amount=19836071332282,
        post_token_amount=20873581936809,
        program_id=None,
    )


@pytest.fixture
def swap_event_from_logs_second(tx_event_from_logs_second) -> SwapEvent:
    """Second SwapEvent matching the commented example (#2)."""
    return SwapEvent(
        user_pubkey="5b9tuvErmHAXpfGNv4wyRDQx6mLhYp4tKry52gxhToBa",
        swap_mode="ExactIn",
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="6NqXBdXA38ZXEGU7nGfp9Fr4JSTKgtfZDqZit91Dbonk",
        amount=50000000,
        ui_amount=0.05,
        timestamp=1756531032,
        amount_pct=None,
        swap_in_type="qty",
        priority_fee=0.0001,
        slippage_bps=250,
        by="copytrade",
        dynamic_slippage=False,
        min_slippage_bps=None,
        max_slippage_bps=None,
        program_id=None,
        tx_event=tx_event_from_logs_second,
    )


@pytest.fixture
def tx_event_from_logs_third() -> TxEvent:
    """Third TxEvent instance derived from logged example (#3)."""
    return TxEvent(
        signature="4CL5kwExbe7JkFFjmGvTqdrpKhV8kjWkpZKy7ovR2GWU2dFBMJEXaBAfVBApzgAxNVKbSaNzuk7SZjnQbvwSyfZf",
        from_amount=5092044280,
        from_decimals=9,
        to_amount=8883051365766,
        to_decimals=6,
        mint="7iCcjyC8NWooMmpjwaAuFPG7ZeGvSwDjKRMPcNdei3ve",
        who="DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        tx_type=TxType.OPEN_POSITION,
        tx_direction="buy",
        timestamp=1756687287,
        pre_token_amount=0,
        post_token_amount=8883051365766,
        program_id="cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG",
    )


@pytest.fixture
def swap_event_from_logs_third(tx_event_from_logs_third) -> SwapEvent:
    """Third SwapEvent matching the commented example (#3)."""
    return SwapEvent(
        user_pubkey="5b9tuvErmHAXpfGNv4wyRDQx6mLhYp4tKry52gxhToBa",
        swap_mode="ExactIn",
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="7iCcjyC8NWooMmpjwaAuFPG7ZeGvSwDjKRMPcNdei3ve",
        amount=50000000,
        ui_amount=0.05,
        timestamp=1756687287,
        amount_pct=None,
        swap_in_type="qty",
        priority_fee=0.0001,
        slippage_bps=250,
        by="copytrade",
        dynamic_slippage=False,
        min_slippage_bps=None,
        max_slippage_bps=None,
        program_id="cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG",
        tx_event=tx_event_from_logs_third,
    )


@pytest.fixture
def tx_event_from_logs_fourth() -> TxEvent:
    """Fourth TxEvent instance derived from logged example (#4)."""
    return TxEvent(
        signature="37URoS3xVL5BYgH7SYb7AdQz5gzAPph366ZKFP779CeiQRKbbzZnuYm1MgFaJ1ZmbPSWxLoo36USSr4hY8QSZWpX",
        from_amount=1424953722,
        from_decimals=9,
        to_amount=42923062985000,
        to_decimals=6,
        mint="6nAvJcCLUJKffEXDRZ4SzgHcssgZJYxJ6j5xbj4qpump",
        who="suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        tx_type=TxType.OPEN_POSITION,
        tx_direction="buy",
        timestamp=1757642156,
        pre_token_amount=0,
        post_token_amount=42923062985000,
        program_id="6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
    )


@pytest.fixture
def swap_event_from_logs_fourth(tx_event_from_logs_fourth) -> SwapEvent:
    """Fourth SwapEvent matching the commented example (#4)."""
    return SwapEvent(
        user_pubkey="5b9tuvErmHAXpfGNv4wyRDQx6mLhYp4tKry52gxhToBa",
        swap_mode="ExactIn",
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="6nAvJcCLUJKffEXDRZ4SzgHcssgZJYxJ6j5xbj4qpump",
        amount=50000000,
        ui_amount=0.05,
        timestamp=1757642156,
        amount_pct=None,
        swap_in_type="qty",
        priority_fee=0.002,
        slippage_bps=3000,
        by="copytrade",
        dynamic_slippage=False,
        min_slippage_bps=None,
        max_slippage_bps=None,
        program_id="6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
        tx_event=tx_event_from_logs_fourth,
    )


@pytest.fixture
def tx_event_from_logs_fifth() -> TxEvent:
    """Fifth TxEvent instance derived from updated logged example (#5)."""
    return TxEvent(
        signature="3AA8G5B5KQa2MBHbPYcWNwzK76gdAVb2De5ooiXtKA6y2jSkFjApNHQMGoRfsHX7btrZ1g82FjxQa9nFqpcMVzN8",
        from_amount=95827897,
        from_decimals=9,
        to_amount=679708083051,
        to_decimals=6,
        mint="Conovv7mKcmj1UnPSccVoUVqPZMZqXDATJ1JGY7oEj2j",
        who="suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        tx_type=TxType.ADD_POSITION,
        tx_direction="buy",
        timestamp=1757651257,
        pre_token_amount=30666413513140,
        post_token_amount=31346121596191,
        program_id="6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
    )


@pytest.fixture
def swap_event_from_logs_fifth(tx_event_from_logs_fifth) -> SwapEvent:
    """Fifth SwapEvent matching the updated commented example (#5)."""
    return SwapEvent(
        user_pubkey="5b9tuvErmHAXpfGNv4wyRDQx6mLhYp4tKry52gxhToBa",
        swap_mode="ExactIn",
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="Conovv7mKcmj1UnPSccVoUVqPZMZqXDATJ1JGY7oEj2j",
        amount=50000000,
        ui_amount=0.05,
        timestamp=1757651257,
        amount_pct=None,
        swap_in_type="qty",
        priority_fee=0.002,
        slippage_bps=250,
        by="copytrade",
        dynamic_slippage=False,
        min_slippage_bps=None,
        max_slippage_bps=None,
        program_id="6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
        tx_event=tx_event_from_logs_fifth,
    )