import pytest

#from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from src.shared.schemas.auth_schema import ChangePassword, UserRegister
from src.domain.services.auth_service import AuthService
from src.infrastructure.db.models import User

@pytest.mark.asyncio
async def test_update_user_password(db_session):
    login = "admin2@gmail.com"
    password="password_123"
    
    new_user_data = ChangePassword(
        login=login,
        current_password=password,
        new_password="password_1234"
    )
    
    user_data = User(
        username="admin",
        password=password,
        phone="+79996315018",
        email="admin2@gmail.com"
    )
    
    db_session.add(user_data)
    await db_session.flush()
    await db_session.refresh(user_data)
    
    await AuthService.update_user_password(new_user_data, db_session)
    
    result = await db_session.execute(select(User)
                .where(
                        User.email == login
                ))
    user = result.scalars().first()
    
    assert user is not None, "Такого пользователя нет"
    assert user.password != new_user_data.new_password, "Парол не обновился"
    
@pytest.mark.asyncio
async def test_find_user_registration(db_session):
    email="admin3@gmail.com"
    username="admin3"
    phone="+79956314803"
    
    user_schema = UserRegister(
        email=email,
        username=username,
        phone=phone,
        password="password_123"
    )
    
    user = User(
        email=email,
        username=username,
        phone=phone,
        password="password_123"
    )
    
    db_session.add(user)
    await db_session.flush()
    
    found_user = await AuthService.find_user_registration(user_schema, db_session)
    
    assert found_user is not None, "Такого пользователя не существует"
    assert found_user.email == email
    assert found_user.phone == phone
    assert found_user.username == username