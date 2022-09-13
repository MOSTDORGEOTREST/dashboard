from fastapi import APIRouter
from api.staff import router as staff_router
from api.prize import router as prize_router
from api.work import router as work_router

router = APIRouter()
router.include_router(staff_router)
router.include_router(prize_router)
router.include_router(work_router)