import db
import models
from db import get_session
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    # Usar base de datos en memoria para cada test
    test_engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    # Parchear el engine global en db.py y models.py
    original_db_engine = db.engine
    original_models_engine = models.engine
    db.engine = test_engine
    models.engine = test_engine

    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)

    # Restaurar engines originales
    db.engine = original_db_engine
    models.engine = original_models_engine


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
