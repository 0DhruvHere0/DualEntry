from fastapi import APIRouter
router = APIRouter(tags=["Health"])
@router.get("/")
def health_check():
    return {
        "project": "DualEntry",
        "version": "1.0.0",
        "status": "Running"
    }