from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from db.crud import create_grammar, get_grammar
from grammar.grammarUtils import extractGrammar
from db import models
from db.database import engine
from dependencies import get_db
import os
env = os.getenv("ENV")

def get_application() -> FastAPI:
    app = FastAPI(
        title="Grammar Extractor Service",
        description="""Extracts grammar patterns from Chinese text""",
        version="0.1.0",
    )

    class ChatMessage(BaseModel):
        message: str

    @app.post("/extract")
    async def extract(chatMessage: ChatMessage, conversationId: str = Query(...), db: Session = Depends(get_db),):
        grammarExtracted, _ = extractGrammar(chatMessage.message)
        for grammar in grammarExtracted:
            grammarExists = get_grammar(
                db, conversation_id=conversationId, pattern=grammar['rule'])
            if grammarExists is None:
                create_grammar(db, conversation_id=conversationId,
                               pattern=grammar['rule'], level=str(grammar['level']))
        return {'grammars': grammarExtracted}
    
    return app
if env != 'TEST':
    models.Base.metadata.create_all(bind=engine)
    app = get_application()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8005"],
        allow_credentials=True,
        allow_methods=["POST"],
        allow_headers=["*"],
    )
