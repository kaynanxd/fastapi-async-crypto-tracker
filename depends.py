
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import AsyncGenerator 
from database.connection import async_session
from fastapi.security import OAuth2PasswordBearer
from auth_user import UserUseCases
from database.models import User

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = async_session()
    try:
        yield session
    finally:
        await session.close()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

async def token_verifier(
    token: str = Depends(oauth_scheme), 
    db_session: AsyncSession = Depends(get_db_session)
) -> User: 
    
    uc = UserUseCases(db_session=db_session)
    
    user = await uc.verify_token(access_token=token)

    return user