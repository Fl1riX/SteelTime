import pytest
from datetime import datetime, timedelta, timezone

from src.presentation.api.v1.auth.dependencies import get_active_user
from src.domain.models.user_model import User
from src.domain.models.ban_model import Ban
from src.presentation.api.v1.exceptions import NoAccess

@pytest.mark.asyncio
async def test_get_active_user_with_active_ban():
    now = datetime.now(timezone.utc)
    user = User(
        id = 1,
        username = "kaka553",
        phone = "+79996543218",
        email = "test@test.test",
        password="test_password",
    )
    ban = Ban(
        reason = "test",
        user_id = 1,
        banned_at = now - timedelta(days=1),
        expires_at = now + timedelta(days=1),
        banned_by=1
    )
    
    user.bans.append(ban)
    
    with pytest.raises(NoAccess):
        await get_active_user(user)
    
@pytest.mark.asyncio
async def test_get_active_user_without_active_ban():
    user = User(
        id = 1,
        username = "kaka553",
        phone = "+79996543218",
        email = "test@test.test",
        password="test_password",
    )
    
    active_user = await get_active_user(user)
    
    assert active_user == user, "Пользователь не найден"