from fastapi.responses import JSONResponse
from datetime import datetime
import uuid
from codes import Codes


def success_response(message: str, code: Codes, data=None):
    return JSONResponse(
        status_code=200,
        content={
            "data": data,
            "message": message,
            "meta": {
                "code": code,
                "traceId": uuid.uuid4().hex,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )


def error_response(status_code: int, message: str, code: Codes):
    return JSONResponse(
        status_code=status_code,
        content=
        {
            "error": {
                "message": message,
                "code": code,
            },
            "meta": {
                "traceId": uuid.uuid4().hex,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )
