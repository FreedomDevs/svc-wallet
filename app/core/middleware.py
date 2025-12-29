from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.utils import generate_trace_id

class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id")
        if not trace_id:
            trace_id = generate_trace_id()
        request.state.trace_id = trace_id
        response = await call_next(request)
        return response
