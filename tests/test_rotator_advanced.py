import pytest

from jemini.core.exceptions import QuotaExceededException
from jemini.rotator.rotator import APIKeyRotator
from jemini.rotator.router import TaskTier
from jemini.storage.models import KeyType


@pytest.mark.asyncio
async def test_free_tier_priority_over_paid():
    rotator = APIKeyRotator()
    rotator.register_key("paid_key_1", key_type=KeyType.PAID)
    rotator.register_key("free_key_1", key_type=KeyType.FREE)
    rotator.register_key("free_key_2", key_type=KeyType.FREE)

    # First requests must strictly pick free keys
    res1 = await rotator.get_active_key(tier=TaskTier.ROUTINE)
    res2 = await rotator.get_active_key(tier=TaskTier.ROUTINE)
    
    assert res1.key_type == KeyType.FREE
    assert res2.key_type == KeyType.FREE
    assert {res1.key_string, res2.key_string} == {"free_key_1", "free_key_2"}

@pytest.mark.asyncio
async def test_model_specific_cooldown_isolation():
    rotator = APIKeyRotator(default_cooldown_seconds=10.0)
    rotator.register_key("solo_key", key_type=KeyType.FREE)

    # 429 arrives on heavy model (COMPLEX tier: gemini-2.5-pro)
    with pytest.raises(QuotaExceededException):
        await rotator.handle_429("solo_key", model_name="gemini-2.5-pro", retry_after=10.0, tier=TaskTier.COMPLEX)

    # The SAME key MUST still be available for light routine model (ROUTINE tier: gemini-2.5-flash)
    routine_res = await rotator.get_active_key(tier=TaskTier.ROUTINE)
    assert routine_res.key_string == "solo_key"
    assert routine_res.model_name == "gemini-2.5-flash"

@pytest.mark.asyncio
async def test_hot_standby_failover_to_paid():
    rotator = APIKeyRotator(default_cooldown_seconds=10.0)
    rotator.register_key("free_key", key_type=KeyType.FREE)
    rotator.register_key("paid_backup_key", key_type=KeyType.PAID)

    # Free key is active
    first = await rotator.get_active_key(tier=TaskTier.COMPLEX)
    assert first.key_string == "free_key"

    # Free key hits 429 -> Hot Standby seamlessly switches to paid backup key!
    fallback = await rotator.handle_429("free_key", model_name="gemini-2.5-pro", tier=TaskTier.COMPLEX)
    assert fallback.key_string == "paid_backup_key"
    assert fallback.key_type == KeyType.PAID
