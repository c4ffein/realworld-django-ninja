from ninja import Schema, ModelSchema, Field
from pydantic import AfterValidator, ConfigDict, EmailStr, field_validator, ValidationInfo
from datetime import datetime

from accounts.schemas import ProfileSchema
from articles.models import Article



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
        fields = ['slug', 'title']

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


class ArticleInCreateSchema(ModelSchema):
    summary: str = Field(alias="description")
    content: str = Field(alias="body")
    tags: list[str] = Field(alias="tagList")

    class Meta:
        model = Article
        fields = ["title"]


class ArticleCreateSchema(Schema):
    article: ArticleInCreateSchema


class ArticleInUpdateSchema(ModelSchema):
    summary: str = Field(alias="description")
    content: str = Field(alias="body")

    class Meta:
        model = Article
        fields = ["title"]


class ArticleUpdateSchema(Schema):
    article: ArticleInUpdateSchema
