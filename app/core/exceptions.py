# app/core/exceptions.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

class FactoryBaseException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

async def global_exception_handler(request: Request, exc: Exception):
    # Log the full error here for headquarters to trace
    status_code = 500
    code = "INTERNAL_SERVER_ERROR"
    message = str(exc)

    if isinstance(exc, FactoryBaseException):
        status_code = exc.status_code
        code = exc.code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error_code": code, "message": message, "trace_id": request.headers.get("X-Request-ID")}
    )