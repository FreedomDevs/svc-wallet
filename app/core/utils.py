import uuid as uuid_lib
from datetime import datetime

def generate_trace_id() -> str:
    return uuid_lib.uuid4().hex

def get_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"
