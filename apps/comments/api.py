from typing import Any

from articles.models import Article
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import AuthorizationError

from comments.models import Comment
from comments.schemas import CommentContainerSchemaIn, CommentOutSchema
from helpers.jwt_utils import AuthedRequest, TokenAuth

router = Router()


@router.get("/articles/{slug}/comments", auth=TokenAuth(pass_even=True), response={200: Any, 404: Any})
def list_comments(request, slug: str) -> dict[str, Any]:
    article = get_object_or_404(Article, slug=slug)
    comments = Comment.objects.filter(article=article).select_related("author").order_by("-created")
    return {"comments": [CommentOutSchema.from_orm(c, context={"request": request}) for c in comments]}


@router.post("/articles/{slug}/comments", auth=TokenAuth(), response={201: Any, 404: Any, 401: Any})
def create_comment(request: AuthedRequest, data: CommentContainerSchemaIn, slug: str) -> tuple[int, dict[str, Any]]:
    article = get_object_or_404(Article, slug=slug)
    comment = Comment.objects.create(
        article=article,
        author=request.user,
        content=data.comment.body,
    )
    return 201, {"comment": CommentOutSchema.from_orm(comment, context={"request": request})}


@router.delete(
    "/articles/{slug}/comments/{comment_id}", auth=TokenAuth(), response={204: None, 404: Any, 403: Any, 401: Any}
)
def delete_comment(request: AuthedRequest, slug: str, comment_id: int) -> HttpResponse:
    get_object_or_404(Article, slug=slug)
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user and comment.article.author != request.user:
        raise AuthorizationError
    comment.delete()
    return HttpResponse(status=204)
