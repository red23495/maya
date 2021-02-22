from fastapi import APIRouter
from .test_suite import router as test_suite_router
from .test_case import router as test_case_router
from .request import router as request_router
router = APIRouter()

router.include_router(router=test_suite_router, prefix='/test_suite')
router.include_router(router=test_case_router, prefix='/test_case')
router.include_router(router=request_router, prefix='/request')

