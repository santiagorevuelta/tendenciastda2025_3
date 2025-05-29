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
        # Calcular tiempo de respuesta
        duration = time.time() - request.start_time

        # Loggear información de la solicitud
        log_data = {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration': duration,
            'user': getattr(request.user, 'username', 'anonymous'),
            'remote_addr': request.META.get('REMOTE_ADDR'),
        }

        logger.info(
            f"{request.method} {request.path} - Status: {response.status_code} "
            f"- Duration: {duration:.2f}s - User: {log_data['user']}"
        )

        # Loggear errores
        if response.status_code >= 400:
            logger.error(
                f"Error {response.status_code} on {request.method} {request.path} - "
                f"User: {log_data['user']} - IP: {log_data['remote_addr']}"
            )

        return response