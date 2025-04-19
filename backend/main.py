from datetime import datetime
from typing import Union
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from app.database import engine, SessionLocal, get_db
from app import models
from sqlalchemy.orm import Session

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Request model for appointment creation
class AppointmentCreate(BaseModel):
    name: str
    created_at: datetime

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    appointments = db.query(models.Appointment).filter(models.Appointment.is_deleted == False).all()
    return {"appointments": appointments}

@app.post("/appointments")
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        db_appointment = models.Appointment(
            name=appointment.name,
            created_at=appointment.created_at,
            is_deleted=False
        )
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))