from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.account import router as account_router
from app.api.routes.user import router as user_router
from app.api.routes.transaction import router as transaction_router
from app.api.routes.counterpart import router as counterpart_router
from app.api.routes.report import router as report_router
router = APIRouter()
router.include_router(health_router)
router.include_router(account_router)
router.include_router(user_router)
router.include_router(transaction_router)
router.include_router(counterpart_router)
router.include_router(report_router)