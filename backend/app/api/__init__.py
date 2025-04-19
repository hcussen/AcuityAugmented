from fastapi import APIRouter

from app.api.routes import general, webhooks

api_router = APIRouter()

# Include all the router modules
api_router.include_router(general.router)
api_router.include_router(webhooks.router)
