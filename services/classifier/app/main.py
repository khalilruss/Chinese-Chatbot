from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, Query
from fastapi.responses import HTMLResponse
from classification_model.word_level_classifier import WordLevelClassifier
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from db.crud import create_word, get_word
from db import models
from db.database import engine
from dependencies import get_db
import os
env = os.getenv("ENV")

def get_application() -> FastAPI:
    app = FastAPI(
        title="Classifier Service",
        description="""Classifies the HSK level of Chinese words""",
        version="0.1.0",
    )

    classifier = WordLevelClassifier()

    class ChatMessage(BaseModel):
        message: str

    @app.post("/classify")
    async def classifySentence(chatMessage: ChatMessage, conversationId: str = Query(...), db: Session = Depends(get_db)):
        classifications = classifier.classify(chatMessage.message)
        for classification in classifications:
            wordExists = get_word(
                db, conversation_id=conversationId, word=classification['word'])
            if wordExists is None:
                create_word(db, conversation_id=conversationId,
                            word=classification['word'], level=str(classification['level']))
        return {'classifications': classifications}

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
