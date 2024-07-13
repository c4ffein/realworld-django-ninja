from ninja import Schema, ModelSchema, Field
from pydantic import SerializeAsAny, validator
from datetime import datetime

from accounts.schemas import ProfileSchema
from articles.models import Article


EMPTY = object()


class ArticleOutSchema(ModelSchema):
    description: str = Field(alias="summary")
    body: str = Field(alias="content")
    createdAt: datetime = Field(alias="created")
    updatedAt: datetime = Field(alias="updated")
    favorited: bool
    favoritesCount: int
    author: ProfileSchema
    tagList: list[str]

    class Meta:
        model = Article
        fields = ["slug", "title"]

    @staticmethod
    def resolve_favorited(obj, context) -> bool:
        user = context.get("request").user
        return obj.favorites.filter(pk=user.id).exists() if user and user.is_authenticated else False

    @staticmethod
    def resolve_favoritesCount(obj) -> int:
        return obj.favorites.count()

    @staticmethod
    def resolve_tagList(obj):
        return obj.tags if isinstance(obj.tags, list) else [t.name for t in obj.tags.all()]


class ArticleInCreateSchema(Schema):
    title: str
    summary: str = Field(alias="description")
    content: str = Field(alias="body")
    tags: SerializeAsAny[list[str]] = Field(EMPTY, alias="tagList")

    @validator("content", "summary", "title")
    def check_not_empty(cls, v):
        assert v != "", "can't be blank"
        return v


class ArticleCreateSchema(Schema):
    article: ArticleInCreateSchema


class ArticleInPartialUpdateSchema(Schema):
    title: SerializeAsAny[str] = EMPTY
    summary: SerializeAsAny[str] = Field(EMPTY, alias="description")
    content: SerializeAsAny[str] = Field(EMPTY, alias="body")

    @validator("content", "summary", "title")
    def check_not_empty(cls, v):
        assert v != "", "can't be blank"
        return v


class ArticlePartialUpdateSchema(Schema):
    article: ArticleInPartialUpdateSchema
