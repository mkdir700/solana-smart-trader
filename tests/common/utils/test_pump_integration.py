"""Test Pump.fun token detection. Integration test connects to the network."""
import pytest
from solbot_common.config import settings
from solbot_common.utils.pump import is_pumpfun_token

pytestmark = [pytest.mark.asyncio] #, pytest.mark.integration]


@pytest.fixture(autouse=True)
def _require_shyft_api_key():
    if not settings.api.shyft_api_key:
        pytest.skip("Missing SHYFT API key (settings.api.shyft_api_key)")


@pytest.mark.parametrize(
    "mint_address,expected",
    [
        # Likely Pump.fun token examples
        ("GFUgXbMeDnLkhZaJS3nYFqunqkFNMRo9ukhyajeXpump", True),
        # Well-known non-pump tokens
        ("So11111111111111111111111111111111111111112", False),  # WSOL
        ("7iCcjyC8NWooMmpjwaAuFPG7ZeGvSwDjKRMPcNdei3ve", False),  # Meteora Token
    ],
)
async def test_is_pumpfun_token_integration(mint_address, expected):
    assert await is_pumpfun_token(mint_address) is expected



