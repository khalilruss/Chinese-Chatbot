from sqlalchemy.orm import Session
from db import models
from db import crud
from api import schemas
from collections import namedtuple
from datetime import timedelta, datetime

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_get_account_by_username(db_session: Session):
    test_account = models.Account(
        username='test', password='test', fullname='test', email='test')
    db_session.add(test_account)
    db_session.commit()
    db_user = crud.get_account_by_username(
        db_session, username=test_account.username)
    assert db_user.username == test_account.username
    assert db_user.password == test_account.password
    assert db_user.fullname == test_account.fullname
    assert db_user.email == test_account.email

def test_check_username_password_correct(db_session: Session):
    hashed_password = pwd_context.hash('test'.encode('utf-8'))
    test_account = models.Account(
        username='test', password=hashed_password, fullname='test', email='test')
    db_session.add(test_account)
    db_session.commit()

    Login = namedtuple('Login', ['username', 'password'])
    login_user = Login('test', 'test')

    assert crud.check_username_password(db_session, login_user) == True

def test_check_username_password_incorrect(db_session: Session):
    hashed_password = pwd_context.hash('test'.encode('utf-8'))
    test_account = models.Account(
        username='test', password=hashed_password, fullname='test', email='test')
    db_session.add(test_account)
    db_session.commit()

    Login = namedtuple('Login', ['username', 'password'])
    login_user = Login('test', '1234')

    assert crud.check_username_password(db_session, login_user) == False

def test_create_account(db_session: Session):
    assert len(db_session.query(models.Account).all()) == 0
    Account = namedtuple(
        'Account', ['username', 'password', 'fullname', 'email'])
    new_account = Account(username='test', password='test',
                          fullname='test', email='test@test.com')
    crud.create_account(db_session, new_account)
    db_account = db_session.query(models.Account).all()

    assert len(db_account) == 1
    assert db_account[0].username == new_account.username
    assert db_account[0].fullname == new_account.fullname
    assert db_account[0].email == new_account.email

def test_get_conversation_history(db_session: Session):
    convo1Time = datetime.now()
    convo2Time = datetime.now() + timedelta(minutes=10)
    test_account = models.Account(
        username='test', password='test', fullname='test', email='test')
    test_converstaion1 = models.Conversation(
        account_id=1, status='Inactive', start_time=convo1Time, end_time=convo1Time + timedelta(minutes=10), duration=10)
    test_converstaion2 = models.Conversation(
        account_id=1, status='Inactive', start_time=convo2Time, end_time=convo2Time + timedelta(minutes=5), duration=5)
    test_word1 = models.Word(conversation_id=1, word="你", level='1')
    test_grammar1 = models.Grammar(conversation_id=1,
                                   pattern="没有/没 (+ Obj.)", level='1')
    test_word2 = models.Word(conversation_id=2, word="你", level='1')
    test_grammar2 = models.Grammar(conversation_id=2,
                                   pattern="没有/没 (+ Obj.)", level='1')
    db_session.add(test_account)
    db_session.add(test_converstaion1)
    db_session.add(test_converstaion2)
    db_session.add(test_word1)
    db_session.add(test_grammar1)
    db_session.add(test_word2)
    db_session.add(test_grammar2)
    db_session.commit()

    conversations = crud.get_conversation_history(
        db_session, test_account.username)
    assert len(conversations) == 2

def test_get_active_conversation(db_session: Session):
    convoTime = datetime.now()
    test_account = models.Account(
        username='test', password='test', fullname='test', email='test')
    test_converstaion = models.Conversation(
        account_id=1, status='Active', start_time=convoTime)
    db_session.add(test_account)
    db_session.add(test_converstaion)
    db_session.commit()

    converstaion = crud.get_active_conversation(
        db_session, test_account.username)

    assert converstaion.account_id == 1
    assert converstaion.status == 'Active'
    assert converstaion.start_time == convoTime

def test_create_conversation(db_session: Session):
    assert len(db_session.query(models.Conversation).all()) == 0
    convoTime = datetime.now()
    test_account = models.Account(
        username='test', password='test', fullname='test', email='test')
    db_session.add(test_account)
    db_session.commit()

    crud.create_conversation(db_session, test_account.username, convoTime)
    db_conversation = db_session.query(models.Conversation).all()

    assert len(db_conversation) == 1
    assert db_conversation[0].account_id == 1
    assert db_conversation[0].start_time == convoTime

def test_end_conversation(db_session: Session):
    convoTime = datetime.now()
    convoEndTime = convoTime + timedelta(minutes=10)
    test_account = models.Account(
        username='test', password='test', fullname='test', email='test')
    test_converstaion = models.Conversation(
        account_id=1, status='Active', start_time=convoTime)
    db_session.add(test_account)
    db_session.add(test_converstaion)
    db_session.commit()

    crud.end_conversation(db_session, test_account.username, convoEndTime, 10)

    db_all_convo = db_session.query(models.Conversation).all()
    db_active_convo = db_session.query(models.Conversation).filter(
        models.Conversation.status == 'Active').all()
    db_inactive_convo = db_session.query(models.Conversation).filter(
        models.Conversation.status == 'Inactive').all()

    assert len(db_all_convo) == 1
    assert len(db_active_convo) == 0
    assert len(db_inactive_convo) == 1
    assert db_inactive_convo[0].account_id == 1
    assert db_inactive_convo[0].start_time == convoTime
    assert db_inactive_convo[0].end_time == convoEndTime
    assert db_inactive_convo[0].duration == 10

def test_delete_conversation(db_session: Session):
    convoTime = datetime.now()
    test_account = models.Account(
        username='test', password='test', fullname='test', email='test')
    test_converstaion = models.Conversation(
        account_id=1, status='Active', start_time=convoTime)
    db_session.add(test_account)
    db_session.add(test_converstaion)
    db_session.commit()

    assert len(db_session.query(models.Conversation).all()) == 1
    crud.delete_conversation(db_session, 1)
    assert len(db_session.query(models.Conversation).all()) == 0
