# backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = str(Path(__file__).parent.parent)
if backend_path not in sys.path:
    sys.path.append(backend_path)

from main import app
from app.database import Base, get_db
from app.config import settings
from app.core.acuityClient import get_acuity_client, AcuityClient
# Import all models to ensure they are registered with SQLAlchemy Base
from app.models import Appointment, Event, Snapshot

# Override the database URL for testing
TEST_DATABASE_URL = "sqlite+pysqlite:///test.db"

# Create test database engine
@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    print(f"\nSetting up test database at: {TEST_DATABASE_URL}")
    
    # Override the database URL in settings
    settings.database_url = TEST_DATABASE_URL
    
    # Create test engine with echo for debugging
    test_engine = create_engine(TEST_DATABASE_URL, echo=True)
    
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=test_engine)
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    print("\nCreated tables:", Base.metadata.tables.keys())
    
    yield test_engine
    
    # Cleanup: drop all tables after tests
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(engine):
    """Create a fresh database session for each test"""
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def client(db_session):
    """Create test client with database session override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up dependency override
    app.dependency_overrides.clear()

@pytest.fixture
def mock_acuity():
    """Create a mock Acuity client for testing"""
    class MockAcuityClient:
        def __init__(self):
            self.appointments = {}
        
        def get_appointment(self, id: str, mock: bool = False):
            return self.appointments.get(id)
        
        def add_appointment(self, appt_data: dict):
            self.appointments[appt_data["id"]] = appt_data
    
    mock_client = MockAcuityClient()
    
    # Store original client
    original_client = get_acuity_client()
    
    # Replace with mock
    # Override the acuity_client in the app
    app.dependency_overrides[get_acuity_client] = lambda: mock_client
    
    yield mock_client
    
    # Restore original client
    if get_acuity_client in app.dependency_overrides:
        del app.dependency_overrides[get_acuity_client]

@pytest.fixture
def create_test_appointment(db_session):
    """Fixture to create test appointments in the database"""
    def _create_appointment(id: str, start_time, canceled: bool = False):
        appt = Appointment(
            id=id,
            start_time=start_time,
            canceled=canceled
        )
        db_session.add(appt)
        db_session.commit()
        return appt
    return _create_appointment