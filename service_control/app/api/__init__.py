from fastapi import APIRouter
from api.reports import router as report_router

router = APIRouter()
router.include_router(report_router)