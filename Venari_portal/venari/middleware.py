# middleware.py

import logging

logger = logging.getLogger(__name__)

class AdminLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the admin action
        if request.user.is_authenticated and request.user.is_staff:
            logger.info(f"Admin {request.user.username} accessed {request.path}")

        response = self.get_response(request)
        return response
