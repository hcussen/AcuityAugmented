from typing import Union
from app.database import engine
from app import models

from fastapi import FastAPI
app = FastAPI()

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Your routes and other FastAPI code...

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}