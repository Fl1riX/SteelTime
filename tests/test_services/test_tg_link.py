import pytest

from datetime import datetime, timedelta
#from unittest.mock import patch, AsyncMock
from sqlalchemy import select

from src.domain.services.tg_link_service import TgLinkService
#from src.domain.services.auth_service import AuthService
from src.domain.db.models import MagicTokens, User

@pytest.mark.asyncio
async def test_save_link_token(db_session):
    """Тест сохрарнения magic токена в БД"""
    # ========= ARRANGE (Подготовка) ==========
    token = "test_token_12412"
    expires = datetime.now() + timedelta(minutes=10)

    # ========= ACT (Действие) ===========
    await TgLinkService.save_link_token(
        token=token,
        expires_at=expires,
        telegram_id=1237459614,
        db=db_session
    )
    
    # ======== Assert (Проверка) ==========
    # читаем из бд
    result = await db_session.execute(
        select(MagicTokens).where(
            MagicTokens.token == token
        )
    )
    saved_token = result.scalar_one()
    
    assert saved_token.telegram_id == 1237459614
    assert saved_token.used is False
    assert saved_token.expires_at > datetime.now()

@pytest.mark.asyncio
async def test_find_token(db_session):
    """Ищет токен в БД"""
    test_token = MagicTokens(
        telegram_id=1239517536,
        token="test_token_779",
        expires_at=datetime.now() + timedelta(minutes=10)
    )
    
    db_session.add(test_token)
    await db_session.commit()
    
    found = await TgLinkService.find_token(token="test_token_779", db=db_session)
    
    assert found is True
    
@pytest.mark.asyncio
async def test_link_account(db_session):
    """Привязываем телеграм бота к аккаунту"""
    test_token = MagicTokens(
        telegram_id=1239517536,
        token="test_token_779",
        expires_at=datetime.now() + timedelta(minutes=10)
    )
    test_user = User(id=1, email="admin@gmail.com", phone="+79999513641", username="admin", password="password_123")
    
    db_session.add(test_token)
    db_session.add(test_user)
    await db_session.commit()
    
    await TgLinkService.link_account(
        db=db_session, 
        link_token=test_token, 
        user=test_user
    )
    
    result = await db_session.execute(
        select(MagicTokens).where(
            MagicTokens.token == "test_token_779"
        )
    )
    linked_token = result.scalar_one()
    
    assert linked_token.used is True
    assert linked_token.telegram_id == 1239517536
    
    

