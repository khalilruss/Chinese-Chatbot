# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from ..db import models, crud
from collections import namedtuple
import jwt
from datetime import datetime
import asynctest
import json
import unittest
import websockets

def test_register(app: FastAPI, db_session: Session, client: TestClient):
    assert len(db_session.query(models.Account).all()) == 0
    response = client.post("/register",
                           json={"fullname": "test", "username": "test", "email": "test@test.com", "password": "1234"})
    assert response.status_code == 201
    assert response.cookies['csrf_refresh_token'] != None
    assert response.cookies['refresh_token_cookie'] != None
    assert jwt.decode(response.cookies['refresh_token_cookie'],
                      "testing", algorithms="HS256")['sub'] == 'test'
    assert jwt.decode(response.json()['access_token'], "testing", algorithms="HS256")[
        'sub'] == 'test'

    db_account = db_session.query(models.Account).all()

    assert len(db_account) == 1
    assert db_account[0].username == "test"
    assert db_account[0].fullname == "test"
    assert db_account[0].email == "test@test.com"

def test_register_existing_username(app: FastAPI, db_session: Session, client: TestClient):
    test_account = models.Account(
        username='test', password='test', fullname='test', email='test@test.com')
    db_session.add(test_account)
    db_session.commit()
    response = client.post("/register",
                           json={"fullname": "test", "username": "test", "email": "test@test.com", "password": "1234"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Username already in use"}


def test_login(app: FastAPI, db_session: Session, client: TestClient):
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    response = client.post("/login",
                           json={"username": "test", "password": "test"})
    assert response.status_code == 200
    assert response.cookies['csrf_refresh_token'] != None
    assert response.cookies['refresh_token_cookie'] != None
    assert jwt.decode(response.cookies['refresh_token_cookie'],
                      "testing", algorithms="HS256")['sub'] == 'test'
    assert jwt.decode(response.json()['access_token'], "testing", algorithms="HS256")[
        'sub'] == 'test'

def test_login_incorrect_username(app: FastAPI, db_session: Session, client: TestClient):
    assert len(db_session.query(models.Account).all()) == 0
    response = client.post("/login",
                           json={"username": "test", "password": "1234"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Username does not exist"}

def test_login_incorrect_password(app: FastAPI, db_session: Session, client: TestClient):
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    response = client.post("/login",
                           json={"username": "test", "password": "1234"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Password entered is incorrect"}


def test_refresh(app: FastAPI, db_session: Session, client: TestClient):
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    response1 = client.post("/login",
                            json={"username": "test", "password": "test"})
    assert response1.status_code == 200

    headers = {'X-CSRF-TOKEN': response1.cookies['csrf_refresh_token']}
    cookies = dict(
        refresh_token_cookie=response1.cookies['refresh_token_cookie'])
    response2 = client.post("/refresh", headers=headers, cookies=cookies)
    assert response2.status_code == 200
    assert jwt.decode(response2.json()['access_token'], "testing", algorithms="HS256")[
        'sub'] == 'test'
def test_refresh_no_csrf_token(app: FastAPI, db_session: Session, client: TestClient):
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    response1 = client.post("/login",
                            json={"username": "test", "password": "test"})
    assert response1.status_code == 200

    response2 = client.post("/refresh")
    assert response2.status_code == 401
    assert response2.json()['detail'] == 'Missing CSRF Token'

def test_refresh_no_refesh_cookie(app: FastAPI, db_session: Session, client: TestClient):
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    response1 = client.post("/login",
                            json={"username": "test", "password": "test"})
    assert response1.status_code == 200

    cookies = dict(
        refresh_token_cookie=" ")
    headers = {'X-CSRF-TOKEN': response1.cookies['csrf_refresh_token']}
    response2 = client.post("/refresh", headers=headers, cookies=cookies)
    assert response2.status_code == 401
    assert response2.json()['detail'] == 'Missing cookie refresh_token_cookie'


def test_logout(app: FastAPI, db_session: Session, client: TestClient):
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    response1 = client.post("/login",
                            json={"username": "test", "password": "test"})
    assert response1.status_code == 200

    headers = {'Authorization': "Bearer " + response1.json()['access_token']}
    response2 = client.delete("/logout", headers=headers)
    assert response2.status_code == 200

def test_logout_no_access_token(app: FastAPI, db_session: Session, client: TestClient):
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    response1 = client.post("/login",
                            json={"username": "test", "password": "test"})
    assert response1.status_code == 200

    response2 = client.delete("/logout")
    assert response2.status_code == 401
    assert response2.json()['detail'] == 'Missing cookie access_token_cookie'

def test_classify(app: FastAPI, db_session: Session, client: TestClient):

    def mock_post(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code
                self.content = bytes(json.dumps(json_data), 'utf-8')

            def json(self):
                return self.json_data

        return MockResponse({"classifications": [{"word": "你", "level": 1}, {"word": "好", "level": 1}]}, 200)

    with asynctest.mock.patch("httpx.AsyncClient.post", side_effect=mock_post):

        Account = namedtuple(
            'Account', ['username', 'password', 'fullname', 'email'])
        new_account = Account(username='test', password='test',
                              fullname='test', email='test@test.com')
        crud.create_account(db_session, new_account)
        response1 = client.post("/login",
                                json={"username": "test", "password": "test"})
        assert response1.status_code == 200

        crud.create_conversation(
            db_session, new_account.username, datetime.now())

        headers = {'Authorization': "Bearer " +
                   response1.json()['access_token']}
        response2 = client.post(
            "/classify", headers=headers, json={"message": "你好"})
        assert response2.status_code == 200
        assert response2.json() == {"classifications": [
            {"word": "你", "level": 1}, {"word": "好", "level": 1}]}

def test_classify_no_conversation(app: FastAPI, db_session: Session, client: TestClient):
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    response1 = client.post("/login",
                            json={"username": "test", "password": "test"})
    assert response1.status_code == 200

    headers = {'Authorization': "Bearer " + response1.json()['access_token']}
    response2 = client.post(
        "/classify", headers=headers, json={"message": "你好"})
    assert response2.status_code == 404
    assert response2.json()['detail'] == 'No active converstaion'

def test_classify_no_access_token(app: FastAPI, db_session: Session, client: TestClient):
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    response1 = client.post("/login",
                            json={"username": "test", "password": "test"})
    assert response1.status_code == 200

    response2 = client.post("/classify", json={"message": "你好"})
    assert response2.status_code == 401
    assert response2.json()['detail'] == 'Missing cookie access_token_cookie'


def test_extract(app: FastAPI, db_session: Session, client: TestClient):

    def mock_post(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code
                self.content = bytes(json.dumps(json_data), 'utf-8')

            def json(self):
                return self.json_data

        return MockResponse({"grammars": [
            {"rule": "没有/没 (+ Obj.)", "level": 1}, {"rule": "Subj. + Verb (+ Obj.) ", "level": 1}]}, 200)

    with asynctest.mock.patch("httpx.AsyncClient.post", side_effect=mock_post):

        Account = namedtuple(
            'Account', ['username', 'password', 'fullname', 'email'])
        new_account = Account(username='test', password='test',
                              fullname='test', email='test@test.com')
        crud.create_account(db_session, new_account)
        response1 = client.post("/login",
                                json={"username": "test", "password": "test"})
        assert response1.status_code == 200

        crud.create_conversation(
            db_session, new_account.username, datetime.now())

        headers = {'Authorization': "Bearer " +
                   response1.json()['access_token']}
        response2 = client.post(
            "/extract", headers=headers, json={"message": "我没有问题。"})
        assert response2.status_code == 200
        assert response2.json() == {"grammars": [
            {"rule": "没有/没 (+ Obj.)", "level": 1}, {"rule": "Subj. + Verb (+ Obj.) ", "level": 1}]}

def test_extract_no_conversation(app: FastAPI, db_session: Session, client: TestClient):
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    response1 = client.post("/login",
                            json={"username": "test", "password": "test"})
    assert response1.status_code == 200

    headers = {'Authorization': "Bearer " + response1.json()['access_token']}
    response2 = client.post("/extract", headers=headers,
                            json={"message": "你好"})
    assert response2.status_code == 404
    assert response2.json()['detail'] == 'No active converstaion'


def test_extract_no_access_token(app: FastAPI, db_session: Session, client: TestClient):
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    response1 = client.post("/login",
                            json={"username": "test", "password": "test"})
    assert response1.status_code == 200

    response2 = client.post("/extract", json={"message": "你好"})
    assert response2.status_code == 401
    assert response2.json()['detail'] == 'Missing cookie access_token_cookie'