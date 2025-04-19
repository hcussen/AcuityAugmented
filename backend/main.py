from typing import Union
from fastapi import FastAPI, Depends
from app.database import engine, get_db
from app import models
from sqlalchemy.orm import Session

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Your API",
    description="Your API description",
    version="0.1.0",
)

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    appointments = db.query(models.Appointment).filter(models.Appointment.is_deleted == False).all()
    return {"appointments": appointments}
