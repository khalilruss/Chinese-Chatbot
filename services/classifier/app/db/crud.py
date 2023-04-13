from sqlalchemy.orm import Session
from .models import Word

def create_word(db: Session, word: str, conversation_id: str, level: str):
    db_word = Word(conversation_id=conversation_id,
                   word=word, level=level)
    db.add(db_word)
    db.commit()

def get_word(db: Session, word: str, conversation_id: str):
    return db.query(Word).filter(Word.word == word, Word.conversation_id == conversation_id).first()
