import pytest
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, String, Table, MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import TIME, TIMESTAMP


def test_timezone_handling(db_session):
    """Test that PostgreSQL handles timezone information correctly."""
    # Create a temporary model with timezone-aware columns
    class Base(DeclarativeBase):
        pass
    
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