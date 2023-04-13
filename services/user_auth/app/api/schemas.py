from typing import List
from pydantic import BaseModel
import os
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

class AccountBase(BaseModel):
    username: str

class AccountCreate(AccountBase):
    fullname: str
    email: str
    password: str

class AccountLogin(AccountBase):
    password: str

class Account(AccountBase):
    id: int

    class Config:
        orm_mode = True

class ChatMessage(BaseModel):
        message:str

class Settings(BaseModel):
    authjwt_secret_key: str = ACCESS_TOKEN_SECRET
    authjwt_token_location: set =('headers','cookies')
    authjwt_cookie_csrf_protect: bool = True
    authjwt_cookie_samesite: str = 'lax'
