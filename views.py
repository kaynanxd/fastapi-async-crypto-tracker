from fastapi import APIRouter, HTTPException, Depends,status
from fastapi.responses import JSONResponse
from schemas import UserCreateImput
from services import UserServices,FavoriteServices,AssetService
from schemas import StandardOutput,ErroOutput,UserFavoriteAdd,UserList,DaySummaryOutput
from typing import List
from asyncio import gather
from sqlalchemy.ext.asyncio import AsyncSession
from depends import get_db_session,token_verifier
from auth_user import UserUseCases
from fastapi.security import OAuth2PasswordRequestForm 
from schemas import UserCreateImput
from passlib.context import CryptContext

user_router=APIRouter(prefix="/user")
assets_router = APIRouter(prefix="/assets")


@user_router.post("/create", description="rota para criar usuarios",response_model=StandardOutput, responses={400:{ "model": ErroOutput}})
async def user_create(user: UserCreateImput, db_session:AsyncSession = Depends(get_db_session)): 
    try:
        uc= UserUseCases(db_session=db_session)
        await uc.user_register(user_schema=user) 
        return JSONResponse(
            content={ "message":"sucesso"},status_code=status.HTTP_201_CREATED
        )
    except Exception as error:
       if isinstance(error, HTTPException):
           raise error
       raise HTTPException(status_code=500, detail=str(error))

@user_router.post("/add/cryptos")
async def add_favorite(symbol: str, user=Depends(token_verifier)):
    try:
        await FavoriteServices.add_favorite(user.id, symbol)
        return {"message": "Crypto adicionada"}
    except Exception as error:
        raise HTTPException(400,detail=str(error))


@user_router.post("/login")
async def user_login(
    request_form_user: OAuth2PasswordRequestForm = Depends(), 
    db_session: AsyncSession = Depends(get_db_session)
):
    try:
        uc = UserUseCases(db_session=db_session)
        
        user_data = UserCreateImput(
            username=request_form_user.username,
            password=request_form_user.password
        )
    
        auth_data = await uc.user_login(user_schema=user_data)
        
        return JSONResponse(
            content=auth_data,
            status_code=status.HTTP_200_OK
        )
    except HTTPException as e:
        raise e
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

@user_router.get("/me")
async def get_me(user=Depends(token_verifier)):
    return {
        "id": user.id,
        "username": user.username,
        "favorites": [f.symbol for f in user.favorites]
    }

@user_router.get("/me/cryptos")
async def list_my_favorites(user=Depends(token_verifier)):
    return [f.symbol for f in user.favorites]


@user_router.put("/update-password")
async def update_password(new_password: str, user=Depends(token_verifier), db=Depends(get_db_session)):
    crypt_context=CryptContext(schemes=["sha256_crypt"])
    user.password = crypt_context.hash(new_password)
    db.add(user)
    await db.commit()
    return {"message": "Senha atualizada com sucesso"}


@user_router.get("/test-token/")
async def test_user_verify(token_verify= Depends(token_verifier)):
    return "works"

    
@user_router.get("/list-all", description="rota para listar usuarios",
    response_model=List[UserList], 
    responses={400:{ "model": ErroOutput}}
)
async def user_list(): 
    try:
        return await UserServices.list_user()
    except Exception as error:
       raise HTTPException(400,detail=str(error))
    
@assets_router.get("/crypto_day_summary/me", 
                   description="Retorna o resumo diário das cryptos do usuário autenticado", 
                   response_model=List[DaySummaryOutput], 
                   responses={400: {"model": ErroOutput}})
async def day_summary_me(user=Depends(token_verifier)):
    try:
        favorites_symbols = [favorite.symbol for favorite in user.favorites]
        tasks = [AssetService.day_summary(symbol=symbol) for symbol in favorites_symbols]
        return await gather(*tasks)

    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    
    
@user_router.delete("/cryptos/remove", description="Remove uma crypto do usuário ", response_model=StandardOutput)
async def remove_favorite(
    symbol: str,
    user=Depends(token_verifier)
):
    try:
        await FavoriteServices.remove_favorite(user_id=user.id, symbol=symbol)
        return StandardOutput(message=f"{symbol} removido das cryptos.")
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    
        
@user_router.delete("/delete/{user_id}", description="rota para deletar usuarios",response_model=StandardOutput, responses={400:{ "model": ErroOutput}})
async def user_delete(user_id:int):
    try:
        await UserServices.delete_user(user_id)
        return StandardOutput(message="Ok")
    except Exception as error:
       raise HTTPException(400,detail=str(error))



    