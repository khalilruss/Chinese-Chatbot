from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")
env = os.getenv("ENV")

if env != 'TEST':
    address='db'
else:
     address='localhost'

print(address)
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{address}:{port}/{db}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
