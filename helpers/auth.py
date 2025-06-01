from accounts.models import User
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
from ninja.security import HttpBearer
from ninja_jwt.authentication import JWTBaseAuthentication


class AuthJWT(HttpBearer, JWTBaseAuthentication):
    openapi_scheme = "token"  # As settings.NINJA_JWT["AUTH_HEADER_TYPES"] isn't working with this custom class
    user_model = User

    def __init__(self, *args, pass_even: bool = False, **kwargs) -> None:
        self.pass_even = pass_even
        super().__init__(*args, **kwargs)

    def __call__(self, request: HttpRequest) -> AbstractUser | None:
        return super().__call__(request) or self.pass_even

    def authenticate(self, request: HttpRequest, key: str) -> AbstractUser:
        return self.jwt_authenticate(request, token=key)
