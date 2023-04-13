from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Request, Query, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import JSONResponse
from starlette import status
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from datetime import timedelta, datetime
import websockets
import asyncio
from httpx import AsyncClient

from db import models, crud
from api import schemas
from api.api_utils import create_token_response
from db.database import engine
from dependencies import get_db

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
import os
env = os.getenv("ENV")

def get_application() -> FastAPI:
    app = FastAPI(
        title="User Authenication Service",
        description="""Authenticates all requests made to the system""",
        version="0.1.0",
    )
    
    @AuthJWT.load_config
    def get_config():
        return schemas.Settings()

    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request: Request, exc: AuthJWTException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
    
    @app.post("/register", status_code=201)
    def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
        db_account = crud.get_account_by_username(db, username=account.username)
        if db_account:
            raise HTTPException(status_code=401, detail="Username already in use")
        else:
            new_account=crud.create_account(db=db, account=account)
            if new_account is not None:
                access_token, refresh_token, refresh_token_expires =create_token_response(account, Authorize)
                Authorize.set_refresh_cookies(refresh_token,max_age=int(refresh_token_expires.total_seconds()))
                return {"access_token": access_token}
            else: 
                raise HTTPException(status_code=500, detail="An error occurred when trying to register your account")

    @app.post("/login")
    def authenticate_account(account: schemas.AccountLogin, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
        db_account = crud.get_account_by_username(db, username=account.username)
        if db_account is None:
            raise HTTPException(status_code=404, detail="Username does not exist")
        else:
            is_password_correct = crud.check_username_password(db, account)
            if is_password_correct is False:
                raise HTTPException(status_code=401, detail="Password entered is incorrect")
            else:
                access_token, refresh_token, refresh_token_expires =create_token_response(db_account, Authorize)
                Authorize.set_refresh_cookies(refresh_token,max_age=int(refresh_token_expires.total_seconds()))
                return {"access_token": access_token}

    @app.post('/refresh')
    def refresh(Authorize: AuthJWT = Depends()):
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()
        access_token_expires = timedelta(minutes=15)
        new_access_token = Authorize.create_access_token(subject=current_user, expires_time=access_token_expires)
        return {"access_token": new_access_token}

    @app.delete('/logout')
    def logout(Authorize: AuthJWT = Depends()):
        Authorize.jwt_required()
        Authorize.unset_refresh_cookies()
        return {"msg":"Successfully logout"}

    @app.post('/classify')
    async def classify(message: schemas.ChatMessage, response: Response, db: Session = Depends(get_db),Authorize: AuthJWT = Depends()):
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        conversation = crud.get_active_conversation(db, username=current_user)
        if conversation:
            url=f'http://classifier:8001/classify?conversationId={conversation.conversation_id}'
            async with AsyncClient() as client:
                proxy = await client.post(url,json=message.dict())
            response.body = proxy.content
            response.status_code = proxy.status_code
            return response
        else:
            raise HTTPException(status_code=404, detail="No active converstaion")

    @app.post('/extract')
    async def extract(message: schemas.ChatMessage, response: Response, db: Session = Depends(get_db),Authorize: AuthJWT = Depends()):
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        conversation = crud.get_active_conversation(db, username=current_user)
        if conversation:
            url=f'http://grammar_extractor:8002/extract?conversationId={conversation.conversation_id}'
            async with AsyncClient() as client:
                proxy = await client.post(url,json=message.dict())
            response.body = proxy.content
            response.status_code = proxy.status_code
            return response
        else:
            raise HTTPException(status_code=404, detail="No active converstaion")

    @app.get('/conversations')
    def conversations(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        conversations = crud.get_conversation_history(db, username=current_user)
        for conversation in conversations:
            conversation.grammars
            conversation.words
        return {"conversations": conversations}

    ws_chatbot_url = "ws://chatbot:8000/chat"

    async def forward(ws_ui: WebSocket, ws_bot: websockets.WebSocketClientProtocol):
        while True:
            data = await ws_ui.receive_text()
            await ws_bot.send(data)

    async def reverse(ws_ui: WebSocket, ws_bot: websockets.WebSocketClientProtocol):
        while True:
            data = await ws_bot.recv()
            await ws_ui.send_text(data)

    @app.websocket('/chat')
    async def websocket(ws_ui: WebSocket, token: str = Query(...), Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
        await ws_ui.accept()
        Authorize.jwt_required("websocket",token=token)
        decoded_token = Authorize.get_raw_jwt(token)
        current_user = decoded_token['sub']
        activeConversation=crud.get_active_conversation(db, username=current_user)
        if activeConversation is None:
            try:
                startTime = datetime.now()
                crud.create_conversation(db, username=current_user, startTime=startTime)
                async with websockets.connect(ws_chatbot_url) as ws_bot:
                    forward_task = asyncio.create_task(forward(ws_ui, ws_bot))
                    reverse_task = asyncio.create_task(reverse(ws_ui, ws_bot))
                    await asyncio.gather(forward_task, reverse_task)
            except:
                endTime = datetime.now()
                activeConversation=crud.get_active_conversation(db, username=current_user)
                activeConversation.grammars
                activeConversation.words
                if len(activeConversation.grammars)==0 and len(activeConversation.words)==0:
                    crud.delete_conversation(db,conversation_id=activeConversation.conversation_id)
                else:
                    difference = endTime - startTime
                    minutes = int(divmod(difference.total_seconds(), 60)[0])
                    crud.end_conversation(db, username=current_user, endTime=endTime, duration=minutes)
        else:
            error_text="You currently already have an active conversation running. " \
                 "Please either continue that conversation or close it before starting a new one"
            await ws_ui.send_text(error_text)
            await ws_ui.close()

    return app

if env != 'TEST':
    models.Base.metadata.create_all(bind=engine)
    app = get_application()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        # allow_methods=["GET","POST","DELETE"],
        allow_headers=["*"],
    )



