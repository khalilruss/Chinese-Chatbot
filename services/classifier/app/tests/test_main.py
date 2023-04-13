# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from ..classification_model.word_level_classifier import WordLevelClassifier
from ..db.models import Conversation, Word, Account
from unittest.mock import patch

def test_classify_endpoint(app: FastAPI, db_session: Session, client: TestClient):
    conversation_id = 1
    with patch('classification_model.word_level_classifier.parser') as mock:
        mock.word_tokenize.return_value =["你", "好"]
        response = client.post("/classify?conversationId=1",
                            json={"message": "你好"})
        assert response.status_code == 200
        assert response.json() == {"classifications": [
            {"word": "你", "level": 1}, {"word": "好", "level": 1}]}
        
        assert len(db_session.query(Word).filter(Word.word == "你",
                                                Word.conversation_id == conversation_id).all()) == 1
        assert len(db_session.query(Word).filter(Word.word == "好",
                                                Word.conversation_id == conversation_id).all()) == 1

def test_classify_endpoint_no_conversationId(app: FastAPI, db_session: Session, client: TestClient):
    conversation_id = 1

    with patch('classification_model.word_level_classifier.parser') as mock:
        mock.word_tokenize.return_value =["你", "好"]

        response = client.post("/classify",
                            json={"message": "你好"})
        assert response.status_code == 422

def test_classify_endpoint_no_duplicates_added(app: FastAPI, db_session: Session, client: TestClient):
    conversation_id = 1
    test_word = Word(conversation_id=conversation_id, word="你", level='1')
    db_session.add(test_word)
    db_session.commit()

    with patch('classification_model.word_level_classifier.parser') as mock:
        mock.word_tokenize.return_value =["你", "好"]
        
        response = client.post("/classify?conversationId=1",
                            json={"message": "你好"})
        assert response.status_code == 200
        assert response.json() == {"classifications": [
            {"word": "你", "level": 1}, {"word": "好", "level": 1}]}
        assert len(db_session.query(Word).filter(Word.word == "你",
                                                Word.conversation_id == conversation_id).all()) == 1
        assert len(db_session.query(Word).filter(Word.word == "好",
                                                Word.conversation_id == conversation_id).all()) == 1
