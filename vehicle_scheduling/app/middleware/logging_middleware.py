import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import sys


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        
        request_id = f"{int(time.time() * 1000)}"
        
        
        logger.info(f"[{request_id}] Incoming request: {request.method} {request.url.path}")
        logger.info(f"[{request_id}] Client: {request.client.host}")
        
        
        start_time = time.time()
        
        try:
            
            response = await call_next(request)
            
            
            process_time = time.time() - start_time
            
            
            logger.info(f"[{request_id}] Response status: {response.status_code}")
            logger.info(f"[{request_id}] Processing time: {process_time:.4f}s")
            
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            
            process_time = time.time() - start_time
            logger.error(f"[{request_id}] Error: {str(e)}")
            logger.error(f"[{request_id}] Processing time: {process_time:.4f}s")
            raise