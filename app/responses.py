from fastapi.responses import JSONResponse
from datetime import datetime
from app.core.utils import get_timestamp
from app.codes import Codes

def success_response(message: str, code: Codes, data=None, status_code: int = 200, trace_id: str = None):
    return JSONResponse(
        status_code=status_code,
        content={
            "data": data,
            "message": message,
            "meta": {
                "code": code.value,
                "traceId": trace_id,
                "timestamp": get_timestamp()
            }
        }
    )

def error_response(status_code: int, message: str, code: Codes, details=None, trace_id: str = None):
    response_content = {
        "error": {
            "message": message,
            "code": code.value,
        },
        "meta": {
            "traceId": trace_id,
            "timestamp": get_timestamp()
        }
    }
    if details:
        response_content["error"]["details"] = details
    return JSONResponse(
        status_code=status_code,
        content=response_content
    )
