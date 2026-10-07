from fastapi import FastAPI

from backend.app.api.router import router
from backend.app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description="Decision-support API for enterprise change consequence analysis.",
    version=settings.app_version,
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ecct-api",
        "version": settings.app_version,
    }