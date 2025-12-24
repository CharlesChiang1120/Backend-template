import uuid, time
from app.core.logger import logger
async def logging_middleware(request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        "http_request", 
        path=request.url.path, 
        status_code=response.status_code, 
        duration=f"{duration:.4f}s", 
        request_id=request_id
    )
    return response