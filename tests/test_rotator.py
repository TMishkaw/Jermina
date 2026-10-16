import pytest

from jemini.core.exceptions import QuotaExceededException
from jemini.rotator.rotator import APIKeyRotator
from jemini.rotator.router import TaskTier
from jemini.storage.models import KeyType


@pytest.mark.asyncio
async def test_api_key_rotator_round_robin():
    rotator = APIKeyRotator()
    rotator.register_key("key_alpha", key_type=KeyType.FREE)
    rotator.register_key("key_beta", key_type=KeyType.FREE)
    
    k1 = await rotator.get_active_key(tier=TaskTier.ROUTINE)
    k2 = await rotator.get_active_key(tier=TaskTier.ROUTINE)
    k3 = await rotator.get_active_key(tier=TaskTier.ROUTINE)
    
    assert k1.key_string == "key_alpha"
    assert k2.key_string == "key_beta"
    assert k3.key_string == "key_alpha"

@pytest.mark.asyncio
async def test_api_key_rotator_429_hot_standby():
    rotator = APIKeyRotator(default_cooldown_seconds=10.0)
    rotator.register_key("key_one", key_type=KeyType.FREE)
    rotator.register_key("key_two", key_type=KeyType.FREE)
    
    active = await rotator.get_active_key(tier=TaskTier.ROUTINE)
    assert active.key_string == "key_one"
    
    # 429 triggers failover to key_two
    fallback = await rotator.handle_429(active.key_string, model_name=active.model_name, retry_after=10.0)
    assert fallback.key_string == "key_two"
    
    # Both exhausted
    with pytest.raises(QuotaExceededException):
        await rotator.handle_429("key_two", model_name=active.model_name, retry_after=10.0)
