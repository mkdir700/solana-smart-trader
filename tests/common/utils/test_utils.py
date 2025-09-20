import pytest
from solbot_common.constants import PUMP_FUN_PROGRAM
from solbot_common.utils import validate_transaction
from solbot_common.utils.utils import (get_associated_bonding_curve,
                                       get_async_client,
                                       get_bonding_curve_account,
                                       get_bonding_curve_pda,
                                       get_global_account)
from solders.pubkey import Pubkey


def test_get_bonding_curve_pda():
    mint = Pubkey.from_string("7YYfWqoKvZmGfX4MgE9TuTpPZz9waHAUUxshFmwqpump")
    result = get_bonding_curve_pda(mint, PUMP_FUN_PROGRAM)
    assert str(result[0]) == "8o4o1rhJQ2AoCHBRvumBAmbPH9pxrxWCAYBCfEFcniee"
    assert result[1] == 255

def test_get_associated_bonding_curve():
    mint = Pubkey.from_string("7YYfWqoKvZmGfX4MgE9TuTpPZz9waHAUUxshFmwqpump")
    bonding_curve = get_bonding_curve_pda(mint, PUMP_FUN_PROGRAM)
    result = get_associated_bonding_curve(bonding_curve[0], mint)
    assert str(result) == "GDmfeokYLpfG4s1MdLcSYTriEgapkBL4hCupMk5UTRev"

@pytest.mark.asyncio
@pytest.mark.parametrize("mint_address,expected_values", [
    ("7YYfWqoKvZmGfX4MgE9TuTpPZz9waHAUUxshFmwqpump", {
        "virtual_token_reserves": 1072999997348202,
        "virtual_sol_reserves": 30000000087,
        "real_token_reserves": 793099997348202,
        "real_sol_reserves": 87,
        "token_total_supply": 1000000000000000,
        "complete": False
    }),
    ("A7S4UkbpAXSVfG196Qvr8TMvpvx3Lz2Q4X2RecuApump", {
        "virtual_token_reserves": 0,
        "virtual_sol_reserves": 0,
        "real_token_reserves": 0,
        "real_sol_reserves": 0,
        "token_total_supply": 1000000000000000,
        "complete": True
    }),
    ("43PLsLePQVtKWm5ba9KTSHfxKLYo8mfno5CPspWApump", {
        "virtual_token_reserves": 1072207014479888,
        "virtual_sol_reserves": 30022187624,
        "real_token_reserves": 792307014479888,
        "real_sol_reserves": 22187624,
        "token_total_supply": 1000000000000000,
        "complete": False
    }),
    ("2UUrnM29s6aU8e1Wx9wfXyxB5oVWfG645RSCcHRBpump", {
        "virtual_token_reserves": 0,
        "virtual_sol_reserves": 0,
        "real_token_reserves": 0,
        "real_sol_reserves": 0,
        "token_total_supply": 1000000000000000,
        "complete": True
    }), # don't understand whats going on with this one?
    ("7eLVcLZRg7ZuE8SXWqd4KE1zJ2XanWz9iR9YTKPrpump", {
        "virtual_token_reserves": 0,
        "virtual_sol_reserves": 0,
        "real_token_reserves": 0,
        "real_sol_reserves": 0,
        "token_total_supply": 1000000000000000,
        "complete": True
    }),
    ("wHwrwk1UjwGuVzHghotdejfXZACzfjEiNWdSstLpump", {
        "virtual_token_reserves": 0,
        "virtual_sol_reserves": 0,
        "real_token_reserves": 0,
        "real_sol_reserves": 0,
        "token_total_supply": 1000000000000000,
        "complete": True
    }),
    ("G9EQcZGf7bqWQuF3u8g7yy3PmNoFS2AQepbH13jZpump", {
        "virtual_token_reserves": 0,
        "virtual_sol_reserves": 0,
        "real_token_reserves": 0,
        "real_sol_reserves": 0,
        "token_total_supply": 1000000000000000,
        "complete": True
    })
])
async def test_get_bonding_curve_account(mint_address, expected_values):
    client = get_async_client()
    mint = Pubkey.from_string(mint_address)
    result = await get_bonding_curve_account(
        client,
        mint,
        PUMP_FUN_PROGRAM,
    )
    assert result
    bonding_curve, associated_bonding_curve, account = result
    assert account.virtual_token_reserves == expected_values["virtual_token_reserves"]
    assert account.virtual_sol_reserves == expected_values["virtual_sol_reserves"]
    assert account.real_token_reserves == expected_values["real_token_reserves"]
    assert account.real_sol_reserves == expected_values["real_sol_reserves"]
    assert account.token_total_supply == expected_values["token_total_supply"]
    assert account.complete == expected_values["complete"]
    
    
@pytest.mark.asyncio
async def test_get_bonding_curve_account_already_launched():
    client = get_async_client()
    mint = Pubkey.from_string("4u4XBTC3ry6U8nCCKzGnB1euCumAChjn6VEShJuEpump")
    result = await get_bonding_curve_account(
        client,
        mint,
        PUMP_FUN_PROGRAM,
    )
    print(f"result: {result}")
    bonding_curve, associated_bonding_curve, account = result
    print(f"bonding_curve: {bonding_curve}")
    print(f"associated_bonding_curve: {associated_bonding_curve}")
    print(f"account: {account}")
    print(f"account: {account.__dict__}")
    # assert account.discriminator == 6966180631402821399
    # assert account.virtual_token_reserves == 0
    # assert account.virtual_sol_reserves == 0
    # assert account.real_token_reserves == 0
    # assert account.real_sol_reserves == 0
    # assert account.token_total_supply == 1000000000000000
    # assert account.complete


@pytest.mark.asyncio
async def test_get_global_account():
    client = get_async_client()
    result = await get_global_account(client, PUMP_FUN_PROGRAM)
    assert result
    assert result.initialized
    assert str(result.authority) == "FFWtrEQ4B4PKQoVuHYzZq8FabGkVatYzDpEVHsK5rrhF"
    assert str(result.fee_recipient) == "62qc2CNXwrYqQScmEdiZFFAnJR262PxWEuNQtxfafNgV"
    assert result.initial_virtual_token_reserves == 1073000000000000
    assert result.initial_virtual_sol_reserves == 30000000000
    assert result.initial_real_token_reserves == 793100000000000
    assert result.token_total_supply == 1000000000000000
    assert result.fee_basis_points == 100


@pytest.mark.asyncio
async def test_validate_transaction():
    tx_hash = (
        "35AkbgknqZ5W8zb4PKuEaf9WmDN9PtwN4Yvcs52hMU3YerRpWMcqZKo6QTu6BHpQC6gxMXxTHijPK17J956HHV38"
    )
    result = await validate_transaction(tx_hash)
    assert result is True


@pytest.mark.asyncio
async def test_validate_transaction_fail_tx_hash():
    tx_hash = (
        "2fL3qiQSVfVt2Vf5PLTepRw7pV5cgiqoLefvHqddUggfAbokEP9TRVGkdBRYa832RrpfX4PoLWfzo61yJDFGuBrt"
    )
    result = await validate_transaction(tx_hash)
    assert result is False

