# from sqlalchemy import text
# from app.database import engine

# def test_database_connection():
#     try:
#         # Try to create a connection and execute a simple query
#         with engine.connect() as connection:
#             result = connection.execute(text("SELECT 1"))
#             print("✅ Database connection successful!")
#             return True
#     except Exception as e:
#         print(f"❌ Database connection failed: {str(e)}")
#         return False

# if __name__ == "__main__":
#     test_database_connection()

import pytest
from sqlalchemy import text
from app.models import Base

def test_database_connection(db_session):
    """Test that we can connect to the database and perform basic operations."""
    # Try to execute a simple query
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

def test_database_tables(db_session):
    """Test that all tables are created properly."""
    # Get all table names from the metadata
    table_names = Base.metadata.tables.keys()
    print(table_names)
    assert len(table_names) > 0

    # Verify we can query each table
    for table_name in table_names:
        result = db_session.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
        # Just checking if the query executes without error
        assert result is not None