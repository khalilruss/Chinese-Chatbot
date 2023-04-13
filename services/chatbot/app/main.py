from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from chatbot_utils.chatbot import ChatBot

def get_application() -> FastAPI:
    app = FastAPI(
        title="Chatbot Service",
        description="""Converse with chatbot in Chinese""",
        version="0.1.0",
    )

    @app.websocket("/chat")
    async def websocket_endpoint(websocket: WebSocket):
        try:
            chatbot = ChatBot(websocket)
            await chatbot.chat()
        except WebSocketDisconnect:
            print('WebSocket Disconnected')
    
    return app

app = get_application()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)