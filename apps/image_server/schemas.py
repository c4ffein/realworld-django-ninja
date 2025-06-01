from ninja import Schema


class CommentSchemaIn(Schema):
    body: str


class CommentContainerSchemaIn(Schema):
    comment: CommentSchemaIn
