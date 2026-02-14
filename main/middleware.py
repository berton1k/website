from django.shortcuts import redirect
from django.urls import reverse

EXEMPT_PATHS = (
    "/login",
    "/login/discord",
    "/login/discord/callback",
    "/static",
    "/admin",
    "/api",
)

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        for p in EXEMPT_PATHS:
            if path.startswith(p):
                return self.get_response(request)

        if not request.session.get("user"):
            return redirect(reverse("login"))

        return self.get_response(request)
