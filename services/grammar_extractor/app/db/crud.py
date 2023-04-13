from sqlalchemy.orm import Session
from db.models import Grammar

def create_grammar(db: Session, pattern:str,conversation_id: str, level:str):
    db_grammar= Grammar(conversation_id=conversation_id, pattern=pattern,level=level)
    db.add(db_grammar)
    db.commit()

def get_grammar(db: Session,  pattern:str, conversation_id: str):
    return db.query(Grammar).filter(Grammar.pattern == pattern, Grammar.conversation_id == conversation_id).first()