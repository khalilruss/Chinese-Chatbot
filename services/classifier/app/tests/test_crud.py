from sqlalchemy.orm import Session
from ..db.models import Word
from ..db import crud


def test_create_word(db_session: Session):
    assert len(db_session.query(Word).all()) == 0
    conversation_id = 1
    crud.create_word(db_session, conversation_id=conversation_id,
                     word="你", level='1')
    word = db_session.query(Word).all()
    assert len(word) == 1
    assert word[0].word == "你"
    assert word[0].level == "1"
    assert word[0].conversation_id == conversation_id

def test_get_word(db_session: Session):
    conversation_id = 1
    test_word = Word(conversation_id=conversation_id, word="你", level='1')
    db_session.add(test_word)
    db_session.commit()

    word = crud.get_word(db_session, conversation_id=conversation_id, word="你")
    assert word.word == "你"
    assert word.level == "1"
