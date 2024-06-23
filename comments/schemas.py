from ninja import Field, Schema

from comments.models import Comment
from articles.serializers import AuthorSerializer


class CommentSchemaIn(Schema):
    body: str


class CommentContainerSchemaIn(Schema):
    comment: CommentSchemaIn
