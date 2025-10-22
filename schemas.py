from pydantic import BaseModel,field_validator
from typing import List
import re

class UserCreateImput(BaseModel):
    username:str
    password:str

    @field_validator("username")
    def validate_username(cls,value):
        if not re.match("^([a-z]|[0-9]|@)+$", value):
            raise ValueError("username format invalid")
        return value
    


class StandardOutput(BaseModel):
    message:str

class ErroOutput(StandardOutput):
    detail:str

class UserFavoriteAdd(BaseModel):
    user_id:int
    symbol:str

class Favorite(BaseModel):
    id:int
    symbol:str
    user_id:int

    class Config:
        orm__mode =True

class UserList(BaseModel):
    id:int
    username:str
    favorites:List[Favorite]

    class Config:
        orm__mode =True

class DaySummaryOutput(BaseModel):
    highest:float
    lowest:float
    symbol:str
    
