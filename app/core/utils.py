import functools
from app.core.logger import logger

def trace_performance(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        # 自動抓取函數名稱紀錄耗時
        logger.info("performance_trace", func_name=func.__name__, duration=f"{end-start:.4f}s")
        return result
    return wrapper