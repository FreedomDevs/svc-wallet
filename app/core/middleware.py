from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.utils import generate_trace_id
import logging
from datetime import datetime

class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id")
        if not trace_id:
            trace_id = generate_trace_id()
        request.state.trace_id = trace_id
        # Логирование trace_id, endpoint (path), и дата
        log_date = datetime.utcnow().isoformat()
        endpoint = request.url.path
        logging.info(f"[{log_date}] endpoint={endpoint} trace_id={trace_id} method={request.method}")
        response = await call_next(request)
        return response
