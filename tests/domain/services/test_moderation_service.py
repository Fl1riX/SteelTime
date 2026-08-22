import pytest
from sqlalchemy import select, insert
from datetime import datetime, timedelta, timezone

from src.domain.services.moderation_service import ModerationService
from src.shared.schemas.moderation_schema import BanCreate
from src.domain.models.user_model import User, UserRole
from src.domain.models.ban_model import Ban
from src.domain.services.exceptions import BanPrivilegeError, UserAlreadyBanned

@pytest.mark.asyncio
async def test_ban_user(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
    )
    
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    ban_info = BanCreate(
        reason="test ban",
        user_id=test_user.id
    )
    
    result = await ModerationService.ban_user(
        ban_info=ban_info,
        banned_by=test_moder.id,
        db=db_session
    )
    
    assert result is not None
    assert result.user_id == test_user.id
    assert result.banned_by == test_moder.id
    
@pytest.mark.asyncio
async def test_ban_user_by_regular_user(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
    )
    
    test_user_2 = User(
        username="test_user_2",
        phone="+79999999999",
        email="test_user_2@test.test",
        password="test_passwd",
    )
    
    db_session.add(test_user)
    db_session.add(test_user_2)
    
    await db_session.flush()
    
    ban_info = BanCreate(
        reason="test ban",
        user_id=test_user.id
    )
    
    with pytest.raises(BanPrivilegeError):
        await ModerationService.ban_user(
            ban_info=ban_info,
            banned_by=test_user_2.id,
            db=db_session
        )
        
    result = await db_session.execute(
        select(Ban).where(
            Ban.user_id == test_user.id
        )
    )
    ban_exists = result.scalars().one_or_none()
    
    assert ban_exists is None 
        
@pytest.mark.asyncio
async def test_ban_already_banned_user(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
    )
    
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    ban_info = BanCreate(
        reason="test ban",
        user_id=test_user.id
    )
    
    await ModerationService.ban_user(
        ban_info=ban_info,
        banned_by=test_moder.id,
        db=db_session
    )
    
    with pytest.raises(UserAlreadyBanned):
        await ModerationService.ban_user(
            ban_info=ban_info,
            banned_by=test_moder.id,
            db=db_session
        )
        
@pytest.mark.asyncio
async def test_is_user_banned_false(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
    )
    
    db_session.add(test_user)
    await db_session.flush()
    
    result = await ModerationService.is_user_banned(
        user_id=test_user.id,
        db=db_session
    )
    
    assert result is False
    
@pytest.mark.asyncio
async def test_is_user_banned_true(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
    )
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    ban_info = BanCreate(
        reason="test ban",
        user_id=test_user.id
    )
    
    await ModerationService.ban_user(
        ban_info=ban_info,
        banned_by=test_moder.id,
        db=db_session
    )
    
    result = await ModerationService.is_user_banned(
        user_id=test_user.id,
        db=db_session
    )
    
    assert result is True
    
@pytest.mark.asyncio
async def test_ban_user_with_past_expires_at(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
    )
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    ban_info = BanCreate(
        reason="test ban",
        user_id=test_user.id,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1)
    )
    
    with pytest.raises(ValueError):
        await ModerationService.ban_user(
            ban_info=ban_info,
            banned_by=test_moder.id,
            db=db_session
        )
        
    result = await db_session.execute(
        select(Ban).where(
            Ban.user_id == test_user.id
        )
    )
    ban_exists = result.scalars().one_or_none()
    
    assert ban_exists is None 
    
@pytest.mark.asyncio
async def test_is_user_banned_with_expired_ban(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
    )
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    await db_session.execute(
        insert(Ban).values(
            reason="test ban",
            user_id=test_user.id,
            banned_by=test_moder.id,
            banned_at=datetime.now(timezone.utc) - timedelta(days=2),
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
    )
    await db_session.flush()
    
    result = await ModerationService.is_user_banned(
        user_id=test_user.id,
        db=db_session
    )
    
    assert result is False
    
@pytest.mark.asyncio
async def test_is_user_banned_with_revoked_ban(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
    )
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    await db_session.execute(
        insert(Ban).values(
            reason="test ban",
            user_id=test_user.id,
            banned_by=test_moder.id,
            banned_at=datetime.now(timezone.utc) - timedelta(days=2),
            expires_at=None,
            revoked_at=datetime.now(timezone.utc) - timedelta(days=1),
            revoked_reason="test",
            revoked_by=test_moder.id
        )
    )
    await db_session.flush()
    
    result = await ModerationService.is_user_banned(
        user_id=test_user.id,
        db=db_session
    )
    
    assert result is False
    
@pytest.mark.asyncio
async def test_is_user_banned_with_permanent_ban(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
    )
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    ban_info = BanCreate(
        reason="test ban",
        user_id=test_user.id,
        expires_at=None
    )
    
    await ModerationService.ban_user(
        ban_info=ban_info,
        banned_by=test_moder.id,
        db=db_session
    )
    
    result = await ModerationService.is_user_banned(
        user_id=test_user.id,
        db=db_session
    )
    
    assert result is True
    
@pytest.mark.asyncio
async def test_is_ban_possible_moder_to_user(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
    )
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    result = await ModerationService.is_ban_possible(
        moder_id=test_moder.id,
        user_id=test_user.id,
        db=db_session
    )
    
    assert result is True
    
@pytest.mark.asyncio
async def test_is_ban_possible_admin_to_moder(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.ADMIN
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    result = await ModerationService.is_ban_possible(
        moder_id=test_moder.id,
        user_id=test_user.id,
        db=db_session
    )
    
    assert result is True
    
@pytest.mark.asyncio
async def test_is_ban_possible_admin_to_admin(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
        role=UserRole.ADMIN
    )
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.ADMIN
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    result = await ModerationService.is_ban_possible(
        moder_id=test_moder.id,
        user_id=test_user.id,
        db=db_session
    )
    
    assert result is False
    
@pytest.mark.asyncio
async def test_is_ban_possible_moder_to_moder(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    result = await ModerationService.is_ban_possible(
        moder_id=test_moder.id,
        user_id=test_user.id,
        db=db_session
    )
    
    assert result is False
    
@pytest.mark.asyncio
async def test_is_ban_possible_moder_to_admin(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
        role=UserRole.ADMIN
    )
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
        role=UserRole.MODERATOR
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    result = await ModerationService.is_ban_possible(
        moder_id=test_moder.id,
        user_id=test_user.id,
        db=db_session
    )
    
    assert result is False
    
@pytest.mark.asyncio
async def test_is_ban_possible_user_to_admin(db_session):
    test_user = User(
        username="test_user",
        phone="+79897652334",
        email="test@test.test",
        password="test_passwd",
        role=UserRole.ADMIN
    )
    test_moder = User(
        username="test_moder",
        phone="+79999999999",
        email="test_moder@test.test",
        password="test_passwd",
    )
    
    db_session.add(test_user)
    db_session.add(test_moder)
    
    await db_session.flush()
    
    result = await ModerationService.is_ban_possible(
        moder_id=test_moder.id,
        user_id=test_user.id,
        db=db_session
    )
    
    assert result is False
    