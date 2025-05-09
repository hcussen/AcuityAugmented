from sqlalchemy import text
from app.models import Base, Appointment
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import TIMESTAMP

# ============================================================================
# Connection Tests
# ============================================================================
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

# ============================================================================
# Timezone Test
# ============================================================================

def test_timezone_handling(db_session):
    """Test that PostgreSQL handles timezone information correctly."""
    # Create a temporary model with timezone-aware columns
    
    class TimezoneTest(Base):
        __tablename__ = "timezone_test"
        
        id = Column(Integer, primary_key=True)
        naive_datetime = Column(DateTime)  # Regular datetime without timezone info
        aware_datetime = Column(DateTime(timezone=True))  # DateTime with timezone info
        timestamp_tz = Column(TIMESTAMP(timezone=True))  # PostgreSQL timestamptz
        
        def __repr__(self):
            return (f"<TimezoneTest(id={self.id}, "
                   f"naive_datetime={self.naive_datetime}, "
                   f"aware_datetime={self.aware_datetime}, "
                   f"timestamp_tz={self.timestamp_tz})>")
    
    # Create the table
    Base.metadata.create_all(bind=db_session.get_bind())
    
    # Create a timezone-aware datetime (UTC)
    now_utc = datetime.now(timezone.utc)
    
    # Insert test data
    test_record = TimezoneTest(
        naive_datetime=now_utc.replace(tzinfo=None),  # Remove timezone info
        aware_datetime=now_utc,  # Keep timezone info
        timestamp_tz=now_utc,  # PostgreSQL timestamptz
    )
    
    db_session.add(test_record)
    db_session.commit()
    db_session.refresh(test_record)
    
    # Fetch the record back
    result = db_session.query(TimezoneTest).first()
    
    # Print detailed debug info
    print("\nTimezone Test Results:")
    print(f"Original UTC time: {now_utc}")
    print(f"Stored naive_datetime: {result.naive_datetime}")
    print(f"Stored aware_datetime: {result.aware_datetime}")
    print(f"Stored timestamp_tz: {result.timestamp_tz}")
    
    # Assertions - focus on the timestamptz column for timezone tests
    assert result.timestamp_tz is not None
    assert result.timestamp_tz.tzinfo is not None  # Should have timezone info
    
    # Test that timestamptz preserves the correct point in time
    # (May be in a different timezone based on database settings, but same moment)
    time_diff = abs((result.timestamp_tz.replace(tzinfo=timezone.utc) - now_utc).total_seconds())
    assert time_diff < 1  # Less than 1 second difference

# ============================================================================
# API Integration Tests
# ============================================================================

def get_test_appointment():
    return Appointment(
            first_name="Test",
            last_name='Appointment',
            acuity_id=12345,
            start_time=datetime.now(),
            acuity_created_at=datetime.now()
        )
class TestDB_CRUD:
      
    def test_appointment_create_read(self, db_session):
        # Create
        db_session.add(get_test_appointment())
        db_session.commit()
        
        # Read
        queried_appointment = db_session.query(Appointment).first()
        assert queried_appointment is not None
        assert queried_appointment.first_name == "Test"
        assert queried_appointment.last_name == 'Appointment'
        
    def test_create_update_read(self, db_session):
        # Create
        db_session.add(get_test_appointment())
        db_session.commit()
        
        # Read
        queried_appointment = db_session.query(Appointment).first()
        assert queried_appointment is not None

        # Update
        queried_appointment.first_name = "Updated"
        db_session.commit()
        updated_appointment = db_session.query(Appointment).first()
        assert updated_appointment.first_name == 'Updated'
        
    def test_delete(self, db_session):
        # Create
        db_session.add(get_test_appointment())
        db_session.commit()
        
        # Read
        queried_appointment = db_session.query(Appointment).first()
        assert queried_appointment is not None

        # Delete
        db_session.delete(queried_appointment)
        db_session.commit()
        all_appointments = db_session.query(Appointment).scalar()

        assert all_appointments is None