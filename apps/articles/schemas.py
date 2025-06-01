from datetime import datetime

from accounts.schemas import ProfileSchema
from ninja import Field, ModelSchema, Schema
from pydantic import SerializeAsAny, validator

from articles.models import Article
from helpers.empty import EMPTY


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
    def resolve_favorited(obj: Article) -> bool:
        return obj.is_favorite

    @staticmethod
    def resolve_favoritesCount(obj: Article) -> int:
        return obj.num_favorites

    @staticmethod
    def resolve_tagList(obj: Article) -> list[str]:
        return sorted(obj.tags if isinstance(obj.tags, list) else [t.name for t in obj.tags.all()])


class ArticleInCreateSchema(Schema):
    title: str
    summary: str = Field(alias="description")
    content: str = Field(alias="body")
    tags: SerializeAsAny[list[str]] = Field(EMPTY, alias="tagList")

    @validator("content", "summary", "title")
    def check_not_empty(cls, v: str) -> str:
        assert v != "", "can't be blank"
        return v


class ArticleCreateSchema(Schema):
    article: ArticleInCreateSchema


class ArticleInPartialUpdateSchema(Schema):
    title: str | None = None
    summary: str | None = Field(None, alias="description")
    content: str | None = Field(None, alias="body")

    @validator("content", "summary", "title")
    def check_not_empty(cls, v: str | None) -> str | None:
        assert v != "", "can't be blank"
        return v


class ArticlePartialUpdateSchema(Schema):
    article: ArticleInPartialUpdateSchema
