import uuid as uuid_lib
from datetime import datetime
from typing import Optional

class TraceContext:
    _current_trace_id: Optional[str] = None
    @classmethod
    def set_trace_id(cls, trace_id: str):
        cls._current_trace_id = trace_id
    @classmethod
    def get_trace_id(cls) -> str:
        if cls._current_trace_id:
            return cls._current_trace_id
        return uuid_lib.uuid4().hex
    @classmethod
    def reset(cls):
        cls._current_trace_id = None

def generate_trace_id() -> str:
    return uuid_lib.uuid4().hex

def get_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"
