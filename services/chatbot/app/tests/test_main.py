# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import regex as re
from ..main import app

client = TestClient(app)

def test_websocket():
    client = TestClient(app)
    with client.websocket_connect("/chat") as websocket:
        websocket.send_text('你好')
        data = websocket.receive_text()
        assert re.match('\\p{Han}+',data)