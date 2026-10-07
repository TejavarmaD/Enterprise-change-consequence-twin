from fastapi import APIRouter

from backend.app.api.changes import router as changes_router
from backend.app.api.consequences import router as consequences_router


router = APIRouter()

router.include_router(changes_router)
router.include_router(consequences_router)