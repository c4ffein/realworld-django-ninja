"""
These routes don't use Schemas for output.
This is on purpose, to show that it is possible to start that way, and to iterate faster.
This is also why this file is only lightly typed.
"""

from typing import Any

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import AuthorizationError

from accounts.schemas import ProfileSchema
from articles.models import Article
from comments.models import Comment
from comments.schemas import CommentContainerSchemaIn
from helpers.auth import AuthJWT

router = Router()


@router.get("/articles/{slug}/comments", auth=AuthJWT(pass_even=True), response={200: Any, 404: Any})
def list(request, slug: str):
    try:
        return {
            "comments": [
                {
                    "id": c.id,
                    "author": ProfileSchema.from_orm(c.author, context={"request": request}).dict(),
                    "body": c.content,
                    "createdAt": c.created,
                    "updatedAt": c.updated,
                }
                for c in Comment.objects.filter(article=Article.objects.get(slug=slug)).order_by("-created")
            ]
        }
    except Exception:
        return 404, {"errors": {"body": ["Bad Request"]}}


@router.post("/articles/{slug}/comments", auth=AuthJWT(), response={200: Any, 404: Any})
def create(request, data: CommentContainerSchemaIn, slug: str):
    article = get_object_or_404(Article, slug=slug)
    comment = Comment.objects.create(
        article=article,
        author=request.user,
        content=data.comment.body,
    )
    return {
        "comment": {
            "id": comment.id,
            "createdAt": comment.created,
            "updatedAt": comment.updated,
            "body": comment.content,
            "author": ProfileSchema.from_orm(comment.author, context={"request": request}).dict(),
        },
    }


@router.delete("/articles/{slug}/comments/{comment_id}", auth=AuthJWT(), response={204: Any, 404: Any, 403: Any})
def delete(request, slug: str, comment_id: int):
    get_object_or_404(Article, slug=slug)
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user and comment.article.author != request.user:
        raise AuthorizationError
    comment.delete()
    return 204, None
