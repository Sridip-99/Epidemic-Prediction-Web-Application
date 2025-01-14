from django.utils.deprecation import MiddlewareMixin

class UserSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # This middleware should not handle admin paths
        if not request.path.startswith('/admin'):
            request.session_engine = 'django.contrib.sessions.backends.db'
            request.session_cookie_name = 'user_sessionid'
            request.META['CSRF_COOKIE_NAME'] = 'user_csrftoken'

    def process_response(self, request, response):
        if hasattr(request, 'session') and not request.path.startswith('/admin'):
            response.set_cookie('user_sessionid', request.session.session_key)
            if 'CSRF_COOKIE' in request.META:
                response.set_cookie('user_csrftoken', request.META['CSRF_COOKIE'])
        return response
