from testcontainers.compose import DockerCompose
import psycopg2
import time
import os
import requests
from types import ModuleType

COMPOSE_PATH = "./FYP_website"
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")

def get_db_conn():
  conn = psycopg2.connect(
      host="localhost",
      database=db,
      user=user,
      password=password,
      port=port)
  return conn

def setup_module():
  compose = DockerCompose(filepath=COMPOSE_PATH,compose_file_name=["docker-compose.yml", "docker-compose.override.yml"])
  compose.start()
  time.sleep(80)
  return compose, get_db_conn()

def teardown_module(compose):
  if not isinstance(compose, ModuleType):
      compose.stop()

def test_db():
  compose, conn = setup_module()
  cur = conn.cursor()
  cur.execute("SELECT 'test'")
  assert cur.fetchone()[0] == "test", "Database is not running"
  cur.close()
  teardown_module(compose)

def test_core_nlp():
  compose, _ = setup_module()
  data='我没有时间'
  data=data.encode('utf-8')
  response = requests.post("http://localhost:9001/?properties={'annotators': 'tokenize,ssplit,pos', 'outputFormat': 'json'}",
                              data=data)
  assert response.status_code == 200
  assert response.json() == {"sentences": [
    {
      "index": 0,
      "tokens": [
        {
          "index": 1,
          "word": "我",
          "originalText": "我",
          "characterOffsetBegin": 0,
          "characterOffsetEnd": 1,
          "pos": "PN"
        },
        {
          "index": 2,
          "word": "没有",
          "originalText": "没有",
          "characterOffsetBegin": 1,
          "characterOffsetEnd": 3,
          "pos": "VE"
        },
        {
          "index": 3,
          "word": "时间",
          "originalText": "时间",
          "characterOffsetBegin": 3,
          "characterOffsetEnd": 5,
          "pos": "NN"
        }
      ]
    }
  ]
}
  teardown_module(compose)

def test_user_auth_db_access():
  compose, conn = setup_module()
  cur = conn.cursor()

  response = requests.post("http://localhost:8005/register",
                          json={"fullname": "test", "username": "test1", "email": "test@test.com", "password": "1234"})

  assert response.status_code == 201
  cur.execute("SELECT * from account")
  users = cur.fetchmany(2)
  newUser=users[1]
  assert newUser[0] == 2
  assert newUser[1] == "test"
  assert newUser[2] == "test@test.com"
  assert newUser[3] == "test1"
  cur.close()
  teardown_module(compose)

def test_grammar_extractor_db_and_coreNLP_access():
  compose, conn = setup_module()
  cur = conn.cursor()

  response = requests.post("http://localhost:8002/extract?conversationId=1",
                            json={"message": "我没有问题。"})

  assert response.status_code == 200
  assert response.json() == {"grammars": [
      {"rule": "没有/没 (+ Obj.)", "level": 1}, {"rule": "Subj. + Verb (+ Obj.) ", "level": 1}]}

  cur.execute("SELECT * FROM grammar WHERE conversation_id = 1")
  grammars = cur.fetchmany(3)
  assert grammars[1][0] == 2
  assert grammars[1][1] == 1
  assert grammars[1][2] == '没有/没 (+ Obj.)'
  assert grammars[1][3] == '1'

  assert grammars[2][0] == 3
  assert grammars[2][1] == 1
  assert grammars[2][2] == 'Subj. + Verb (+ Obj.) '
  assert grammars[2][3] == '1'
  cur.close()
  teardown_module(compose)

def test_classifier_db_and_coreNLP_access():
  compose, conn = setup_module()
  cur = conn.cursor()

  response = requests.post("http://localhost:8001/classify?conversationId=1",
                          json={"message": "你好"})
  assert response.status_code == 200
  assert response.json() == {"classifications": [
      {"word": "你", "level": 1}, {"word": "好", "level": 1}]}

  cur.execute("SELECT * FROM word WHERE conversation_id = 1")
  words = cur.fetchmany(3)
  assert words[1][0] == 2
  assert words[1][1] == 1
  assert words[1][2] == '你'
  assert words[1][3] == '1'

  assert words[2][0] == 3
  assert words[2][1] == 1
  assert words[2][2] == '好'
  assert words[2][3] == '1'
  cur.close()
  teardown_module(compose)
