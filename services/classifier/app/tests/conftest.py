import os
from typing import Any, Generator

import pytest
from ..main import get_application, get_db
from ..db import models
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Default to using sqlite in memory for fast tests.
# Can be overridden by environment variable for testing in CI against other
# database engines
SQLALCHEMY_DATABASE_URL = "sqlite:///./tests/test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    models.Base.metadata.create_all(engine)  # Create the tables.
    db=Session()
    test_account= models.Account(username='test', password='test', fullname='test', email= 'test')
    test_converstaion= models.Conversation(account_id=1, status='Active', start_time=datetime.now())
    db.add(test_converstaion)
    db.add(test_account)
    db.commit()
    _app =get_application()
    yield _app
    models.Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(app: FastAPI) -> Generator[Session, Any, None]:
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at the end of each test ensuring
    a clean state.
    """

    # connect to the database
    connection = engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection
    session = Session(bind=connection)
    yield session  # use the session in tests.
    session.close()
    # rollback - everything that happened with the
    # Session above (including calls to commit())
    # is rolled back.
    transaction.rollback()
    # return connection to the Engine
    connection.close()


@pytest.fixture()
def client(app: FastAPI, db_session: Session) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client