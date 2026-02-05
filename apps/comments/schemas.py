from datetime import datetime

from accounts.schemas import ProfileSchema
from ninja import Field, ModelSchema, Schema

from comments.models import Comment


class CommentSchemaIn(Schema):
    body: str


class CommentContainerSchemaIn(Schema):
    comment: CommentSchemaIn


class CommentOutSchema(ModelSchema):
    body: str = Field(alias="content")
    createdAt: datetime = Field(alias="created")
    updatedAt: datetime = Field(alias="updated")
    author: ProfileSchema

    class Meta:
        model = Comment
        fields = ["id"]
