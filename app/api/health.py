from fastapi import APIRouter, Request, Depends
from app.responses import success_response
from app.codes import Codes
from app.core.utils import TraceContext
from app.db.session import get_db
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

router = APIRouter(tags=["system"])

@router.get("/live")
async def get_live(request: Request):
    trace_id = request.headers.get("X-Trace-Id")
    TraceContext.set_trace_id(trace_id)
    return success_response(
        data={"alive": True},
        code=Codes.LIVE_OK,
        message="svc-wallet жив"
    )

@router.get("/health")
async def get_health(request: Request, db: AsyncSession = Depends(get_db)):
    trace_id = request.headers.get("X-Trace-Id")
    TraceContext.set_trace_id(trace_id)
    database_status = "OK"
    dependencies = {}
    overall_status = "UP"
    # Check database
    try:
        if db:
            await db.execute("SELECT 1")
        database_status = "OK"
    except Exception:
        database_status = "DOWN"
        overall_status = "DOWN"
    # Check svc-users dependency
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.SVC_USERS_URL}/health", timeout=2.0)
            dependencies["svc-users"] = "OK" if response.status_code == 200 else "DOWN"
            if response.status_code != 200:
                overall_status = "DOWN"
    except Exception:
        dependencies["svc-users"] = "DOWN"
        overall_status = "DOWN"
    return success_response(
        data={
            "status": overall_status,
            "database": database_status,
            "dependencies": dependencies
        },
        code=Codes.HEALTH_OK,
        message="Сервис работает" if overall_status == "UP" else "Сервис имеет проблемы"
    )
