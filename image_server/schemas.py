from ninja import Field, Schema

from comments.models import Comment


class CommentSchemaIn(Schema):
    body: str


class CommentContainerSchemaIn(Schema):
    comment: CommentSchemaIn
