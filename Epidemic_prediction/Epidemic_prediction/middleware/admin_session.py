from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class AdminSessionMiddleware(MiddlewareMixin):
    """
    Middleware to manage separate session and CSRF cookies for admin and regular users.
    """
    def process_request(self, request):
        """
        Dynamically adjust session and CSRF cookie settings based on the user type.
        Admin users (root users) receive separate session and CSRF management.
        """
        if request.path.startswith('/admin'):  # Admin routes
            # Set admin-specific session and CSRF configurations
            request.session_cookie_name = 'admin_sessionid'
            request.META['CSRF_COOKIE_NAME'] = 'admin_csrftoken'
        else:  # Non-admin user routes
            # Set user-specific session and CSRF configurations
            request.session_cookie_name = 'user_sessionid'
            request.META['CSRF_COOKIE_NAME'] = 'user_csrftoken'

    def process_response(self, request, response):
        """
        Ensure appropriate cookies are set in the response for session and CSRF management.
        """
        if hasattr(request, 'session') and request.session.session_key:
            if request.path.startswith('/admin'):  # Admin routes
                response.set_cookie(
                    'admin_sessionid',
                    request.session.session_key,
                    httponly=True,
                    secure=settings.SESSION_COOKIE_SECURE,  # Secure cookie setting from Django settings
                    samesite='Lax'  # Adjust samesite if needed (e.g., Strict or None for cross-domain)
                )
                if 'CSRF_COOKIE' in request.META:
                    response.set_cookie(
                        'admin_csrftoken',
                        request.META['CSRF_COOKIE'],
                        httponly=False  # CSRF cookies must be accessible by JavaScript
                    )
            else:  # Non-admin user routes
                response.set_cookie(
                    'user_sessionid',
                    request.session.session_key,
                    httponly=True,
                    secure=settings.SESSION_COOKIE_SECURE,
                    samesite='Lax'
                )
                if 'CSRF_COOKIE' in request.META:
                    response.set_cookie(
                        'user_csrftoken',
                        request.META['CSRF_COOKIE'],
                        httponly=False
                    )

        return response
