from fastapi import APIRouter, Request, Depends
from app.responses import success_response
from app.codes import Codes
from app.db.session import get_db
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

router = APIRouter(tags=["system"])

@router.get("/live")
async def get_live(request: Request):
    # TraceID теперь устанавливается через middleware
    trace_id = getattr(request.state, 'trace_id', None)
    return success_response(
        data={"alive": True},
        code=Codes.LIVE_OK,
        message="svc-wallet жив",
        trace_id=trace_id
    )

@router.get("/health")
async def get_health(request: Request, db: AsyncSession = Depends(get_db)):
    # TraceID теперь устанавливается через middleware
    trace_id = getattr(request.state, 'trace_id', None)
    database_status = "OK"
    dependencies = {}
    overall_status = "UP"
    # Check database
    import sqlalchemy.exc
    try:
        if db:
            await db.execute("SELECT 1")
        database_status = "OK"
    except (sqlalchemy.exc.SQLAlchemyError, AttributeError):
        database_status = "DOWN"
        overall_status = "DOWN"
    # Check svc-users dependency
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.SVC_USERS_URL}/health", timeout=2.0)
            dependencies["svc-users"] = "OK" if response.status_code == 200 else "DOWN"
            if response.status_code != 200:
                overall_status = "DOWN"
    except (httpx.RequestError, httpx.TimeoutException):
        dependencies["svc-users"] = "DOWN"
        overall_status = "DOWN"
    return success_response(
        data={
            "status": overall_status,
            "database": database_status,
            "dependencies": dependencies
        },
        code=Codes.HEALTH_OK,
        message="Сервис работает" if overall_status == "UP" else "Сервис имеет проблемы",
        trace_id=trace_id
    )
