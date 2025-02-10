import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Workshop, SAMPLE_WORKSHOP_DATA


# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the get_db dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop them after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """Create a fresh database session for a test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def app_with_db():
    """Create app instance with test database"""
    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(app_with_db):
    """Create a test client"""
    with TestClient(app_with_db) as test_client:
        yield test_client


@pytest.fixture
def sample_workshop(db_session):
    """Create a sample workshop in the database"""
    workshop = Workshop(**SAMPLE_WORKSHOP_DATA)
    db_session.add(workshop)
    db_session.commit()
    db_session.refresh(workshop)
    return workshop
