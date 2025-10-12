import httpx
from solbot_cache.cached import cached
from solbot_common.config import settings
from solbot_common.utils.shyft import ShyftAPI


@cached(ttl=None, noself=True)
async def is_pumpfun_token(mint_address):
    shyft_api = ShyftAPI(settings.api.shyft_api_key)
    resp = await shyft_api.get_token_info(mint_address)
    metadata_uri = resp.get('metadata_uri')
    if not metadata_uri:
        return False

    # 2. Fetch the off-chain metadata JSON asynchronously
    async with httpx.AsyncClient(timeout=10.0) as client:
        meta_resp = await client.get(metadata_uri)
        meta_resp.raise_for_status()
        metadata = meta_resp.json()
    created_on = metadata.get("createdOn") or metadata.get("created_on")

    # 3. Check if it originated from pump.fun
    return isinstance(created_on, str) and "pump.fun" in created_on.lower()
    
  