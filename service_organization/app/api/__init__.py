from fastapi import APIRouter
from api.staff import router as users_router
from api.prize import router as prizes_router
from api.work import router as works_router

router = APIRouter()
router.include_router(users_router)
router.include_router(prizes_router)
router.include_router(works_router)
