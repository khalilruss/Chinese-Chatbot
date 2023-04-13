from sqlalchemy.orm import Session
from ..db.models import Grammar
from ..db import crud

def test_create_grammar(db_session: Session):
    assert len(db_session.query(Grammar).all()) == 0
    conversation_id = 1
    crud.create_grammar(db_session, conversation_id=conversation_id,
                        pattern="没有/没 (+ Obj.)", level='1')

    grammar = db_session.query(Grammar).all()
    assert len(grammar) == 1
    assert grammar[0].pattern == "没有/没 (+ Obj.)"
    assert grammar[0].level == "1"
    assert grammar[0].conversation_id == conversation_id

def test_get_grammar(db_session: Session):
    conversation_id = 1
    test_grammar = Grammar(conversation_id=conversation_id,
                           pattern="没有/没 (+ Obj.)", level='1')
    db_session.add(test_grammar)
    db_session.commit()

    grammar = crud.get_grammar(
        db_session, conversation_id=conversation_id, pattern="没有/没 (+ Obj.)")
    assert grammar.pattern == "没有/没 (+ Obj.)"
    assert grammar.level == "1"
