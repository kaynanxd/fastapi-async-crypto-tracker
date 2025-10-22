from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UserCreateImput
from database.models import User
from passlib.context import CryptContext
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError, DBAPIError
from fastapi import status
from jose import jwt, JWTError
from datetime import datetime,timedelta,timezone
from sqlalchemy.future import select



from dotenv import load_dotenv
load_dotenv()

from os import getenv

SECRET_KEY=getenv("SECRET_KEY")
ALGORITHM=getenv("ALGORITHM")

crypt_context=CryptContext(schemes=["sha256_crypt"])

class UserUseCases:
    def __init__(self,db_session:AsyncSession): 
        self.db_session = db_session

    async def user_register(self, user_schema:UserCreateImput): 
            
            user_model = User(
                username=user_schema.username,
                password=crypt_context.hash(user_schema.password)
            )
            
            try:
                self.db_session.add(user_model) 
                await self.db_session.flush() 
                await self.db_session.commit()
                
            except IntegrityError: 
                await self.db_session.rollback() 
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="user já existe")
            except DBAPIError as e: 
                await self.db_session.rollback()
                raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro no banco de dados: {str(e)}")
            
    async def user_login(self, user_schema, expires: int = 30):
        result = await self.db_session.execute(
            select(User).where(User.username == user_schema.username)
        )
        
        user_on_db = result.scalars().first()

        if user_on_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid username or password"
            )
        
        if not crypt_context.verify(user_schema.password, user_on_db.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid username or password"
            )
        exp = datetime.now(timezone.utc) + timedelta(minutes=expires)
        print(f"KEY NA CODIFICAÇÃO: {SECRET_KEY}")
        payload={
              "sub": user_on_db.username,
              "exp":exp
         }

        access_token = jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

        return {
            "access_token": access_token,
            "token_type": "bearer", 
            "exp": exp.isoformat()
        }

    async def verify_token(self, access_token):
        try:
            data = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            
            username = data.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
            )
        
        result = await self.db_session.execute(
            select(User).where(User.username == username)
        )
        
        user_on_db = result.scalars().first()

        if user_on_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário do token não encontrado"
            )
        
        return user_on_db