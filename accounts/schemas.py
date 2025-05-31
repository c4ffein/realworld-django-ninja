from typing import Annotated, Any, Optional

from django.conf import settings
from ninja import ModelSchema, Schema
from pydantic import AfterValidator, EmailStr, ValidationInfo, field_validator

from accounts.models import User
from helpers.empty import EMPTY, _Empty


def none_to_blank(v: Optional[str], info: ValidationInfo) -> str:
    return "" if v is None else v


class ProfileSchema(ModelSchema):
    following: bool
    bio: Optional[str]
    image: str

    class Meta:
        model = User
        fields = ["username"]

    @staticmethod
    def resolve_following(obj: User, context: dict[str, Any]) -> bool:
        user = getattr(context.get("request"), "user", None)
        return obj.followers.filter(pk=user.id).exists() if user and user.is_authenticated else False

    @staticmethod
    def resolve_bio(obj: User, context: dict[str, Any]) -> str | None:
        return obj.bio or None  # ty: ignore[invalid-return-type] - Safe with this Model

    @staticmethod
    def resolve_image(obj: User, context: dict[str, Any]) -> str:
        return obj.image or settings.DEFAULT_USER_IMAGE  # ty: ignore[invalid-return-type] - Safe with this Model


class ProfileOutSchema(Schema):
    profile: ProfileSchema


class UserInCreateSchema(ModelSchema):
    email: EmailStr

    class Meta:
        model = User
        fields = ["email", "password", "username"]

    @field_validator("email", "password", "username", check_fields=False)
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("can't be blank")
        return v


class UserCreateSchema(Schema):
    user: UserInCreateSchema


class UserInLoginSchema(ModelSchema):
    class Meta:
        model = User
        fields = ["email", "password"]

    @field_validator("email", "password", check_fields=False)
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("can't be blank")
        return v


class UserLoginSchema(Schema):
    user: UserInLoginSchema


class UserMineSchema(ModelSchema):
    email: EmailStr

    class Meta:
        model = User
        fields = ["email", "bio", "image", "username"]


class UserGetSchema(Schema):
    user: UserMineSchema


class UserInPartialUpdateInSchema(Schema):
    email: Annotated[Optional[EmailStr] | _Empty, AfterValidator(none_to_blank)] = EMPTY
    bio: Annotated[Optional[str] | _Empty, AfterValidator(none_to_blank)] = EMPTY
    image: Annotated[Optional[str] | _Empty, AfterValidator(none_to_blank)] = EMPTY
    username: Annotated[Optional[str] | _Empty, AfterValidator(none_to_blank)] = EMPTY
    password: Annotated[Optional[str] | _Empty, AfterValidator(none_to_blank)] = EMPTY


class UserPartialUpdateInSchema(Schema):
    user: UserInPartialUpdateInSchema


class UserInPartialUpdateOutSchema(UserMineSchema):
    token: str

    @staticmethod
    def resolve_token(obj: User, context: dict[str, Any] | None) -> str:
        return str(context.get("token", "") if context is not None else "")


class UserPartialUpdateOutSchema(Schema):
    user: UserInPartialUpdateOutSchema
