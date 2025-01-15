import re

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

from django.urls import reverse_lazy

staff_member_required = user_passes_test(lambda u:u.is_staff)

class RequireAdminLoginMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.required = tuple(re.compile(url) for url in settings.ADMIN_LOGIN_REQUIRED_URLS)

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # No need to process URLs if user already logged in
        if request.user.is_staff:
            return None

        for url in self.required:
            if url.match(request.path):
                return staff_member_required(view_func)(request, *view_args, **view_kwargs)

        # Explicitly return None for all non-matching requests
        return None