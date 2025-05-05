from fastapi import FastAPI
from app.api import api_router
from fastapi.middleware.cors import CORSMiddleware

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



# Include all API routes
app.include_router(api_router)
