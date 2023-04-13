# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from ..db.models import Grammar
from unittest.mock import patch


def test_extract_endpoint(app: FastAPI, db_session: Session, client: TestClient):
    conversation_id = 1
    with patch('grammar.grammarUtils.parser') as mock:
        mock.pos_tag.return_value =[('我', 'PN'), ('没有', 'VE'), ('问题', 'NN'), ('。', 'PU')]

        response = client.post("/extract?conversationId=1",
                            json={"message": "我没有问题。"})
        assert response.status_code == 200
        assert response.json() == {"grammars": [
            {"rule": "没有/没 (+ Obj.)", "level": 1}, {"rule": "Subj. + Verb (+ Obj.) ", "level": 1}]}
        assert len(db_session.query(Grammar).filter(Grammar.pattern == "没有/没 (+ Obj.)",
                                                    Grammar.conversation_id == conversation_id).all()) == 1
        assert len(db_session.query(Grammar).filter(Grammar.pattern == "Subj. + Verb (+ Obj.) ",
                                                    Grammar.conversation_id == conversation_id).all()) == 1


def test_extract_endpoint_no_conversationId(app: FastAPI, db_session: Session, client: TestClient):
    conversation_id = 1
    with patch('grammar.grammarUtils.parser') as mock:
        mock.pos_tag.return_value =[('我', 'PN'), ('没有', 'VE'), ('问题', 'NN'), ('。', 'PU')]
        response = client.post("/extract",
                            json={"message": "我没有问题。"})
        assert response.status_code == 422


def test_extract_endpoint_no_duplicates_added(app: FastAPI, db_session: Session, client: TestClient):
    conversation_id = 1
    test_grammar = Grammar(conversation_id=conversation_id,
                           pattern="没有/没 (+ Obj.)", level='1')
    db_session.add(test_grammar)
    db_session.commit()
    with patch('grammar.grammarUtils.parser') as mock:
        mock.pos_tag.return_value =[('我', 'PN'), ('没有', 'VE'), ('问题', 'NN'), ('。', 'PU')]

        response = client.post("/extract?conversationId=1",
                            json={"message": "我没有问题。"})
        assert response.status_code == 200
        assert response.json() == {"grammars": [
            {"rule": "没有/没 (+ Obj.)", "level": 1}, {"rule": "Subj. + Verb (+ Obj.) ", "level": 1}]}
        assert len(db_session.query(Grammar).filter(Grammar.pattern == "没有/没 (+ Obj.)",
                                                    Grammar.conversation_id == conversation_id).all()) == 1
        assert len(db_session.query(Grammar).filter(Grammar.pattern == "Subj. + Verb (+ Obj.) ",
                                                    Grammar.conversation_id == conversation_id).all()) == 1
