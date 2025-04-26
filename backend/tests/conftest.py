import pytest
from fastapi.testclient import TestClient  
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from sqlalchemy.orm import sessionmaker  

import sys
import os
from pathlib import Path

# Add the project root directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.models import Base
from app.database import get_db  
from main import app  
  
def pytest_addoption(parser):  
    """
    this adds the option to run the pytests with --dburl 
    """
    parser.addoption(  
        "--dburl",  # For Postgres use "postgresql://user:password@localhost/dbname"  
        action="store",  
        default="sqlite+pysqlite:///./test.db'",   
        help="Database URL to use for tests.",  
    )  
  
  
@pytest.hookimpl(tryfirst=True)  
def pytest_sessionstart(session):  
    db_url = session.config.getoption("--dburl")  
    try:  
        # Attempt to create an engine and connect to the database.  
        engine = create_engine(  
            db_url,  
        )  
        connection = engine.connect()  
        connection.close()  # Close the connection right after a successful connect.  
        print("Database connection successful........")  
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
    engine = create_engine(  
        db_url,  
    )  
  
    # Create a sessionmaker to manage sessions  
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  
  
    # Create tables in the database  
    Base.metadata.create_all(bind=engine)  
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
        yield test_client  