from fastapi import APIRouter

router = APIRouter()

@router.get("/notifications/{user_id}")
async def getHistory(user_id: str):
    pass