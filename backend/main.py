from fastapi import FastAPI
from app.api import api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from app.core.auth import get_api_key

app = FastAPI(
    title="Your API",
    description="Your API description",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://informed-easily-oryx.ngrok-free.app"],  # Your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods or specify: ["GET", "POST", etc.]
    allow_headers=["*"],  # Allow all headers or specify needed ones
)


# Add a simple root endpoint
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/healthcheck")
def read_root():
     return {"status": "ok"}

@app.get("/protected-endpoint", dependencies=[Depends(get_api_key)])
async def protected_endpoint():
    return {"message": "You have access to the protected endpoint"}


# Include all API routes
app.include_router(api_router)
