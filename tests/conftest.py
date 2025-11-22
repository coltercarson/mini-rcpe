import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
import models

# Use shared in-memory SQLite for testing with StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite://"

@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine with shared memory."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Share the same connection
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(test_engine):
    """Create a test client with test database."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_recipe_data():
    """Sample recipe data for testing."""
    return {
        "title": "Test Recipe",
        "total_time_minutes": 30,
        "base_servings": 4,
        "steps": [
            {
                "step_number": 1,
                "action": "Mix flour and water",
                "time_minutes": 5,
                "tools": ["bowl", "spoon"],
                "ingredients": [
                    {"ingredient_name": "flour", "amount": 2.0, "unit": "cup"},
                    {"ingredient_name": "water", "amount": 1.0, "unit": "cup"}
                ]
            },
            {
                "step_number": 2,
                "action": "Bake in oven",
                "time_minutes": 25,
                "tools": ["oven"],
                "ingredients": []
            }
        ]
    }

@pytest.fixture
def authenticated_client(client):
    """Create an authenticated test client."""
    # Set authentication cookie
    client.cookies.set("session_token", "authenticated")
    return client
