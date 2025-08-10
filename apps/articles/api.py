from typing import Any

from accounts.models import User
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import AuthorizationError
from taggit.models import Tag

from articles.models import Article
from articles.schemas import ArticleCreateSchema, ArticleOutSchema, ArticlePartialUpdateSchema
from helpers.empty import EMPTY
from helpers.exceptions import clean_integrity_error
from helpers.jwt_utils import AuthedRequest, TokenAuth

router = Router()


@router.post("/articles/{slug}/favorite", auth=TokenAuth(), response={200: Any, 404: Any})
def favorite(request: AuthedRequest, slug: str) -> dict[str, Any] | tuple[int, dict[str, Any]]:
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    if article.favorites.filter(id=request.user.id).exists():
        return 409, {"errors": {"body": ["Already Favourited Article"]}}
    article.favorites.add(request.user)
    article = get_object_or_404(Article.objects.with_favorites(request.user), id=article.id)  # Now with updated values
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.delete("/articles/{slug}/favorite", auth=TokenAuth(), response={200: Any, 404: Any})
def unfavorite(request: AuthedRequest, slug: str) -> dict[str, Any]:
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    get_object_or_404(article.favorites, id=request.user.id)
    article.favorites.remove(request.user.id)
    article = get_object_or_404(Article.objects.with_favorites(request.user), id=article.id)  # Now with updated values
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.get("/articles/feed", auth=TokenAuth(), response={200: Any, 404: Any})
def feed(request: AuthedRequest, limit: int = 20, offset: int = 0) -> dict[str, Any]:
    followed_authors = User.objects.filter(followers=request.user)
    queryset = Article.objects.with_favorites(request.user).filter(author__in=followed_authors).order_by("-created")
    articles = list(queryset[offset : offset + limit])
    return {
        "articlesCount": queryset.count(),
        "articles": [ArticleOutSchema.from_orm(a, context={"request": request}) for a in articles],
    }


@router.get("/articles", response={200: Any})
def list_articles(
    request,
    tag: str | None = None,
    author: str | None = None,
    favorited: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    queryset = Article.objects.with_favorites(request.user)
    queryset = queryset.filter(tags__name=tag) if tag else queryset
    queryset = queryset.filter(author__username=author) if author else queryset
    queryset = queryset.filter(favorites__username=favorited) if favorited else queryset
    queryset = queryset.order_by("-created")
    articles = list(queryset[offset : offset + limit])
    return {
        "articles": [ArticleOutSchema.from_orm(a, context={"request": request}) for a in articles],
        "articlesCount": queryset.count(),
    }


@router.post("/articles", auth=TokenAuth(), response={201: Any, 409: Any, 422: Any})
def create_article(request: AuthedRequest, data: ArticleCreateSchema) -> tuple[int, dict[str, Any]]:
    with transaction.atomic():
        try:
            article = Article.objects.create(
                **{k: v for k, v in data.article.dict().items() if k != "tags"},
                author=request.user,
            )
        except IntegrityError as err:
            return 409, {"already_existing": clean_integrity_error(err)}
        if data.article.tags != EMPTY:
            for tag_name in data.article.tags:
                article.tags.add(tag_name)
        article.save()
    article = get_object_or_404(Article.objects.with_favorites(request.user), id=article.id)
    return 201, {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.get("/articles/{slug}", auth=TokenAuth(pass_even=True), response={200: Any, 404: Any})
def retrieve(request, slug: str) -> dict[str, Any]:
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.delete("/articles/{slug}", auth=TokenAuth(), response={200: Any, 204: Any, 404: Any, 403: Any, 401: Any})
def destroy(request: AuthedRequest, slug: str) -> HttpResponse:
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.author:
        raise AuthorizationError
    article.delete()
    # As `return 204, None` would fail with newman outside debug => Content-Length=2 like if we outputed ""
    return HttpResponse(status=204)


@router.put("/articles/{slug}", auth=TokenAuth(), response={200: Any, 404: Any, 403: Any, 401: Any})
def update(request: AuthedRequest, slug: str, data: ArticlePartialUpdateSchema) -> dict[str, Any]:
    """This is wrong, but this method behaves like a PATCH, as required by the RealWorld API spec"""
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    if request.user != article.author:
        raise AuthorizationError
    updated_fields = []
    for attr, value in data.article.dict(exclude_unset=True).items():
        setattr(article, attr, value)
        updated_fields.extend(["title", "slug"] if attr == "title" else [attr])
    article.save(update_fields=updated_fields)  # Prevents some race condition
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.get("/tags", response={200: Any})
def list_tags(request) -> dict[str, Any]:
    return {"tags": [t.name for t in Tag.objects.all()]}
