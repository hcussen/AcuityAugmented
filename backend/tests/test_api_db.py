from datetime import datetime
from app.database import SessionLocal, engine
from app.models import Base, Appointment

def test_api_database_connection():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Create a test appointment
        db = SessionLocal()
        test_appointment = Appointment(
            name="Test Appointment",
            created_at=datetime.now(),
        )
        
        try:
            # Add and commit the test appointment
            db.add(test_appointment)
            db.commit()
            
            # Query the appointment back
            queried_appointment = db.query(Appointment).filter_by(name="Test Appointment").first()
            
            if queried_appointment and queried_appointment.name == "Test Appointment":
                print("✅ API-Database integration test successful!")
                print(f"Created and retrieved appointment: {queried_appointment}")
            else:
                print("❌ Failed to retrieve the test appointment")
                
            # Clean up - delete the test appointment
            db.delete(queried_appointment)
            db.commit()
            
        except Exception as e:
            print(f"❌ Database operation failed: {str(e)}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")

if __name__ == "__main__":
    test_api_database_connection()
