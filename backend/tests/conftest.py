import pytest
import subprocess
import time
from fastapi.testclient import TestClient  
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from sqlalchemy.orm import sessionmaker  
from .mockAcuityClient import MockAcuityClient
from app.core.acuityClient import AcuityClient, acuity_client

import sys
from pathlib import Path
# Add the project root directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.models import Base
from app.database import get_db  
from main import app  
from app.config import settings

# PostgreSQL connection string for tests
POSTGRES_TEST_URL = "postgresql://postgres:postgres@localhost:5433/test_db"

def pytest_addoption(parser):  
    """
    This adds the option to run the pytests with --dburl 
    """
    parser.addoption(  
        "--dburl",
        action="store",  
        default=POSTGRES_TEST_URL,
        help="Database URL to use for tests.",  
    )
    
    parser.addoption(
        "--use-docker",
        action="store_true",
        default=True,
        help="Use Docker for PostgreSQL test database"
    )


@pytest.fixture(scope="session", autouse=True)
def postgres_container(request):
    """Start and stop PostgreSQL container for tests"""
    use_docker = request.config.getoption("--use-docker")
    if not use_docker:
        # Skip Docker setup if not using Docker
        yield
        return

    # Start the PostgreSQL container using docker-compose
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"],
        check=True
    )
    
    # Wait for PostgreSQL to be ready
    max_retries = 5
    for i in range(max_retries):
        try:
            engine = create_engine(POSTGRES_TEST_URL)
            connection = engine.connect()
            connection.close()
            print("PostgreSQL test database is ready")
            break
        except SQLAlchemyOperationalError:
            if i < max_retries - 1:
                print(f"Waiting for PostgreSQL to be ready (attempt {i+1}/{max_retries})...")
                time.sleep(2)
            else:
                subprocess.run(
                    ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
                    check=True
                )
                pytest.exit("Could not connect to PostgreSQL container")
    
    # Continue with tests
    yield
    
    # Stop and remove the container after tests
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
        check=True
    )


@pytest.hookimpl(tryfirst=True)  
def pytest_sessionstart(session):  
    # Skip database check if using Docker, as the postgres_container fixture
    # will handle the connection check
    if session.config.getoption("--use-docker"):
        return
        
    db_url = session.config.getoption("--dburl")  
    try:  
        # Attempt to create an engine and connect to the database.  
        engine = create_engine(db_url)  
        connection = engine.connect()  
        connection.close()  # Close the connection right after a successful connect.  
        print("Database connection successful...")  
    except SQLAlchemyOperationalError as e:  
        print(f"Failed to connect to the database at {db_url}: {e}")  
        pytest.exit(  
            "Stopping tests because database connection could not be established."  
        )  

@pytest.fixture(scope="session")  
def db_url(request):  
    """Fixture to retrieve the database URL."""  
    return request.config.getoption("--dburl")  
  
  
@pytest.fixture(scope="function")  
def db_session(db_url):  
    """Create a new database session with a rollback at the end of the test."""  
    # Create a SQLAlchemy engine  
    engine = create_engine(db_url)  
  
    # Create a sessionmaker to manage sessions  
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  
  
    # Create tables in the database  
    Base.metadata.drop_all(bind=engine)  # Drop all tables first to ensure clean state
    Base.metadata.create_all(bind=engine)  
    
    # Use a transaction that will be rolled back after the test
    connection = engine.connect()  
    transaction = connection.begin()  
    session = TestingSessionLocal(bind=connection)  
    
    yield session  
    
    session.close()  
    transaction.rollback()  
    connection.close()  

@pytest.fixture(scope="function")  
def test_client(db_session):  
    """Create a test client that uses the override_get_db fixture to return a session."""  
  
    def override_get_db():  
        try:  
            yield db_session  
        finally:  
            db_session.close()  
  
    app.dependency_overrides[get_db] = override_get_db  
    with TestClient(app) as test_client:  
        test_client.headers.update({"X-API-Key": settings.api_key})
        yield test_client  


@pytest.fixture
def mock_acuity():
    """Fixture that provides a MockAcuityClient instance"""
    return MockAcuityClient()


@pytest.fixture
def patched_acuity_client(monkeypatch, mock_acuity):
    """Fixture that replaces the singleton acuity_client with our mock"""
    # Replace the global client with our mock
    monkeypatch.setattr("app.core.acuityClient.acuity_client", mock_acuity)
    
    # Also patch any imports of acuity_client in other modules
    monkeypatch.setattr("app.api.routes.acuity.acuity_client", mock_acuity)
    monkeypatch.setattr("app.api.routes.webhook.acuity_client", mock_acuity)
    
    # Also patch the AcuityClient class to return our mock for any new instances
    def mock_init(self):
        self.__dict__ = mock_acuity.__dict__
    monkeypatch.setattr(AcuityClient, "__init__", mock_init)
    
    return mock_acuity