"""Pytest configuration and shared fixtures for testing."""
import pytest
import os
import asyncio
from typing import Generator, AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment variables BEFORE importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-min-32-chars-long"
os.environ["ALGORITHM"] = "HS256"

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User
from app.models.question import Question
from app.core.security import get_password_hash

# Use in-memory SQLite for tests (fast, isolated)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=test_engine)


def override_get_db():
    """Override the database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
def test_user(test_db):
    """Create a test user."""
    user = User(
        phone_number="+23276123456",
        email="test@example.com",
        full_name="Test Student",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_teacher(test_db):
    """Create a test teacher user."""
    teacher = User(
        phone_number="+23276999888",
        email="teacher@example.com",
        full_name="Test Teacher",
        hashed_password=get_password_hash("teacherpass123"),
        is_active=True,
        is_verified=True
    )
    test_db.add(teacher)
    test_db.commit()
    test_db.refresh(teacher)
    return teacher


@pytest.fixture(scope="function")
def test_questions(test_db):
    """Create sample questions for testing."""
    questions = [
        Question(
            subject="Mathematics",
            topic="Algebra",
            content="Solve for x: 2x + 4 = 10",
            options_json='["x = 2", "x = 3", "x = 4", "x = 5"]',
            correct_index=1,
            explanation="Subtract 4 from both sides: 2x = 6, then divide by 2: x = 3",
            difficulty="medium"
        ),
        Question(
            subject="Physics",
            topic="Mechanics",
            content="What is Newton's First Law?",
            options_json='["F=ma", "Every action has equal reaction", "Object at rest stays at rest", "E=mc²"]',
            correct_index=2,
            explanation="Law of Inertia",
            difficulty="easy"
        ),
        Question(
            subject="Chemistry",
            topic="Stoichiometry",
            content="Balance: H2 + O2 → H2O",
            options_json='["2H2 + O2 → 2H2O", "H2 + O2 → H2O", "H2 + 2O2 → H2O", "H2 + O2 → 2H2O"]',
            correct_index=0,
            explanation="2 hydrogen molecules + 1 oxygen molecule → 2 water molecules",
            difficulty="medium"
        )
    ]
    
    for q in questions:
        test_db.add(q)
    test_db.commit()
    
    # Refresh to get IDs
    for q in questions:
        test_db.refresh(q)
    
    return questions


@pytest.fixture(scope="function")
async def auth_headers(client: AsyncClient, test_user) -> dict:
    """Get authentication headers for test user."""
    # OAuth2PasswordRequestForm expects form data, not JSON
    login_data = {
        "username": test_user.phone_number,
        "password": "testpass123"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
async def teacher_headers(client: AsyncClient, test_teacher) -> dict:
    """Get authentication headers for test teacher."""
    login_data = {
        "username": test_teacher.phone_number,
        "password": "teacherpass123"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Configure pytest-asyncio
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test"
    )
