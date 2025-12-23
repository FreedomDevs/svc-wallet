from fastapi import APIRouter
from responses import success_response
from codes import Codes

router = APIRouter(tags=["heals"])

@router.get("/live")
def get_live():
    return success_response(data={"alive": True}, code=Codes.LIVE_OK, message="svc-wallet жив")
