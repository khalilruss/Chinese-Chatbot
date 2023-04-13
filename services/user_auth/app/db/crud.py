
from sqlalchemy.orm import Session
from db.models import Account, Conversation
from api.schemas import AccountCreate, AccountLogin
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_account_by_username(db: Session, username: str):
    return db.query(Account).filter(Account.username == username).first()

def check_username_password(db: Session, account: AccountLogin):
    db_account_info: Account = get_account_by_username(db, username=account.username)
    return pwd_context.verify(account.password.encode('utf-8'), db_account_info.password.encode('utf-8'))
    
def create_account(db: Session, account: AccountCreate):
    hashed_password = pwd_context.hash(account.password.encode('utf-8'))
    db_account = Account(username=account.username, password=hashed_password, fullname=account.fullname, email= account.email)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_conversation_history(db: Session, username: str):
    db_account: Account = get_account_by_username(db, username=username)
    conversations: Conversation= db.query(Conversation).filter(Conversation.account_id==db_account.id, Conversation.status=='Inactive').all()
    return conversations

def get_active_conversation(db: Session, username: str):
    db_account: Account = get_account_by_username(db, username=username)
    return db.query(Conversation).filter(Conversation.account_id==db_account.id, Conversation.status=='Active').first()

def create_conversation(db: Session, username: str, startTime: str):
    db_account: Account = get_account_by_username(db, username=username)
    db_conversation= Conversation(account_id=db_account.id, status='Active', start_time=startTime)
    db.add(db_conversation)
    db.commit()

def end_conversation(db: Session, username: str, endTime: str, duration: int):
    db_account: Account = get_account_by_username(db, username=username)
    db.query(Conversation).filter(Conversation.account_id==db_account.id, Conversation.status=='Active').\
    update({"status": "Inactive","end_time": endTime, "duration": duration}, synchronize_session="fetch")
    db.commit()

def delete_conversation(db: Session, conversation_id: int):
    db.query(Conversation).filter_by(conversation_id=conversation_id).delete()
    db.commit()