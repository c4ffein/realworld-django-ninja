from typing import Any

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import AuthorizationError
from ninja_jwt.tokens import AccessToken

from accounts.models import User
from accounts.schemas import (
    EMPTY,
    ProfileOutSchema,
    ProfileSchema,
    UserCreateSchema,
    UserGetSchema,
    UserInPartialUpdateOutSchema,
    UserLoginSchema,
    UserMineSchema,
    UserPartialUpdateInSchema,
    UserPartialUpdateOutSchema,
)
from helpers.auth import AuthJWT
from helpers.exceptions import clean_integrity_error

router = Router()


@router.post("/users", response={201: Any, 400: Any, 409: Any})
def account_registration(request, data: UserCreateSchema) -> tuple[int, dict[str, Any]]:
    try:
        user = User.objects.create_user(data.user.email, username=data.user.username, password=data.user.password)
    except IntegrityError as err:
        return 409, {"already_existing": clean_integrity_error(err)}
    jwt_token = AccessToken.for_user(user)
    return 201, {
        "user": {
            "username": user.username,
            "email": user.email,
            "bio": user.bio or None,
            "image": user.image or settings.DEFAULT_USER_IMAGE,
            "token": str(jwt_token),
        },
    }


@router.post("/users/login", response={200: Any, 401: Any})
def account_login(request, data: UserLoginSchema) -> dict[str, Any] | tuple[int, dict[str, Any]]:
    user = authenticate(email=data.user.email, password=data.user.password)
    if user is None:
        return 401, {"detail": [{"msg": "incorrect credentials"}]}
    jwt_token = AccessToken.for_user(user)
    return {
        "user": {
            "username": user.username,
            "email": user.email,
            "bio": user.bio or None,
            "image": user.image or settings.DEFAULT_USER_IMAGE,
            "token": str(jwt_token),
        },
    }


@router.get("/user", auth=AuthJWT(), response={200: Any, 404: Any})
def get_user(request) -> UserGetSchema:
    return UserGetSchema.model_construct(user=UserMineSchema.from_orm(request.user))


@router.put("/user", auth=AuthJWT(), response={200: Any, 401: Any})
def put_user(request, data: UserPartialUpdateInSchema) -> UserPartialUpdateOutSchema:
    """This is wrong, but this method behaves like a PATCH, as required by the RealWorld API spec"""
    for word in ("email", "bio", "image", "username"):
        value = getattr(data.user, word)
        if value != EMPTY:
            setattr(request.user, word, value)
    if data.user.password != EMPTY:
        request.user.set_password(data.user.password)
    request.user.save()
    token = AccessToken.for_user(request.user)
    return UserPartialUpdateOutSchema.model_construct(
        user=UserInPartialUpdateOutSchema.from_orm(request.user, context={"token": token}),
    )


@router.get("/profiles/{username}", auth=AuthJWT(pass_even=True), response={200: Any, 401: Any, 404: Any})
def get_profile(request, username: str) -> ProfileOutSchema:
    return ProfileOutSchema.model_construct(
        profile=ProfileSchema.from_orm(get_object_or_404(User, username=username), context={"request": request})
    )


@router.post("/profiles/{username}/follow", auth=AuthJWT(), response={200: Any, 400: Any, 403: Any, 404: Any, 409: Any})
def follow_profile(request, username: str) -> tuple[int, None] | ProfileOutSchema:
    profile = get_object_or_404(User, username=username)
    if profile == request.user:
        raise AuthorizationError
    if profile.followers.filter(pk=request.user.id).exists():
        return 409, None
    profile.followers.add(request.user)
    return ProfileOutSchema.model_construct(profile=ProfileSchema.from_orm(profile, context={"request": request}))


@router.delete(
    "/profiles/{username}/follow", auth=AuthJWT(), response={200: Any, 400: Any, 403: Any, 404: Any, 409: Any}
)
def unfollow_profile(request, username: str) -> tuple[int, None] | ProfileOutSchema:
    profile = get_object_or_404(User, username=username)
    if profile == request.user:
        raise AuthorizationError
    if not profile.followers.filter(pk=request.user.id).exists():
        return 409, None
    profile.followers.remove(request.user)
    return ProfileOutSchema.model_construct(profile=ProfileSchema.from_orm(profile, context={"request": request}))
