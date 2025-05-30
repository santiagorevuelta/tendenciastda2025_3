# middleware/logging_middleware.py
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        duration = time.time() - request.start_time
        
        extra = {
            'user': getattr(request.user, 'username', 'anonymous'),
            'ip': request.META.get('REMOTE_ADDR'),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration': duration
        }
        
        logger.info(
            f"{request.method} {request.path} - Status: {response.status_code}",
            extra=extra
        )

        if response.status_code >= 400:
            logger.error(
                f"Error {response.status_code} on {request.method} {request.path}",
                extra=extra
            )

        return response