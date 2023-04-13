from sqlalchemy import Column, Integer, String, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base

class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String)
    email = Column(String)
    username = Column(String, unique=True)
    password = Column(String)
    conversations = relationship("Conversation")

class Conversation(Base):
    __tablename__ = "conversation"
    conversation_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    status = Column(Enum('Active', 'Inactive',
                         name="STATUS", create_type=False))
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    duration = Column(Integer)

class Grammar(Base):
    __tablename__ = "grammar"
    grammar_id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey(
        'conversation.conversation_id'))
    pattern = Column(String)
    level = Column(Enum('1', '2', '3', '4', '5', '6',
                            name="LEVEL", create_type=False))
