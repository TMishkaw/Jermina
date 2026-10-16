import pytest
from jemini.rotator.rotator import APIKeyRotator
from jemini.core.exceptions import QuotaExceededException

@pytest.mark.asyncio
async def test_api_key_rotator_round_robin():
    rotator = APIKeyRotator(keys=["key_alpha", "key_beta"])
    
    k1 = await rotator.get_active_key()
    k2 = await rotator.get_active_key()
    k3 = await rotator.get_active_key()
    
    assert k1 == "key_alpha"
    assert k2 == "key_beta"
    assert k3 == "key_alpha"

@pytest.mark.asyncio
async def test_api_key_rotator_429_hot_standby():
    rotator = APIKeyRotator(keys=["key_one", "key_two"], default_cooldown=10.0)
    
    active = await rotator.get_active_key()
    assert active == "key_one"
    
    # 429 triggers failover to key_two
    fallback = await rotator.handle_429(active, retry_after=10.0)
    assert fallback == "key_two"
    
    # Both exhausted
    with pytest.raises(QuotaExceededException):
        await rotator.handle_429("key_two", retry_after=10.0)
