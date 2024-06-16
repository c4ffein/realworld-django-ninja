from typing import Any, Optional

from django.http import HttpRequest
from ninja.security import HttpBearer
from ninja_jwt.authentication import JWTBaseAuthentication

from accounts.models import User


class AuthJWT(HttpBearer, JWTBaseAuthentication):
    openapi_scheme = "token"
    user_model = User

    def __init__(self, *args, pass_even=False, **kwargs):
        self.pass_even = pass_even
        super().__init__(*args, **kwargs)

    def __call__(self, request: HttpRequest) -> Optional[Any]:
        return super().__call__(request) or self.pass_even

    def authenticate(self, request, key):
        return self.jwt_authenticate(request, token=key)
