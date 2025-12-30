import logging
import re
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import time

# Custom formatter to mask IPs in logs
class PrivacyLogFormatter(logging.Formatter):
    # Regex to find IPv4 addresses
    IP_PATTERN = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

    def format(self, record):
        message = super().format(record)
        # Mask IP addresses: 127.0.0.1 -> 127.0.0.XXX
        masked_message = self.IP_PATTERN.sub(lambda m: ".".join(m.group().split(".")[:-1]) + ".XXX", message)
        return masked_message

class PrivacyShieldMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Sanitize sensitive headers for logging if needed
        # (FastAPI/Uvicorn doesn't log headers by default, but this is a safety net)
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

def setup_privacy_logging():
    """
    Configure root logger and Uvicorn loggers to use the PrivacyLogFormatter.
    """
    formatter = PrivacyLogFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get all relevant loggers
    loggers = [
        logging.getLogger("uvicorn"),
        logging.getLogger("uvicorn.access"),
        logging.getLogger("uvicorn.error"),
        logging.getLogger("fastapi")
    ]
    
    for logger in loggers:
        for handler in logger.handlers:
            handler.setFormatter(formatter)
