from typing import Any

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from ninja import Router

from accounts.models import User
from helpers.auth import AuthJWT
from helpers.empty import EMPTY
from helpers.exceptions import clean_integrity_error
from taggit.models import Tag

from articles.models import Article
from articles.schemas import ArticleCreateSchema, ArticleOutSchema, ArticlePartialUpdateSchema


router = Router()


@router.post("/articles/{slug}/favorite", auth=AuthJWT(), response={200: Any, 404: Any})
def favorite(request, slug):
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    if article.favorites.filter(id=request.user.id).exists():
        return 409, {"errors": {"body": ["Already Favourited Article"]}}
    article.favorites.add(request.user)
    article = get_object_or_404(Article.objects.with_favorites(request.user), id=article.id)  # Now with updated values
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.delete("/articles/{slug}/favorite", auth=AuthJWT(), response={200: Any, 404: Any})
def unfavorite(request, slug):
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    get_object_or_404(article.favorites, id=request.user.id)
    article.favorites.remove(request.user.id)
    article = get_object_or_404(Article.objects.with_favorites(request.user), id=article.id)  # Now with updated values
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.get("/articles/feed", auth=AuthJWT(), response={200: Any, 404: Any})
def feed(request):
    followed_authors = User.objects.filter(followers=request.user)
    articles = [
        a for a in Article.objects.with_favorites(request.user).filter(author__in=followed_authors).order_by("-created")
    ]
    return {
        "articlesCount": len(articles),
        "articles": [ArticleOutSchema.from_orm(a, context={"request": request}) for a in articles],
    }


@router.get("/articles", response={200: Any})
def list_articles(request):
    return {
        "articles": [
            ArticleOutSchema.from_orm(a, context={"request": request})
            for a in Article.objects.with_favorites(request.user).all()
        ]
    }


@router.post("/articles", auth=AuthJWT(), response={201: Any, 409: Any, 422: Any})
def create_article(request, data: ArticleCreateSchema):
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


@router.get("/articles/{slug}", auth=AuthJWT(pass_even=True), response={200: Any, 404: Any})
def retrieve(request, slug: str):
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.delete("/articles/{slug}", auth=AuthJWT(), response={204: Any, 404: Any, 403: Any, 401: Any})
def destroy(request, slug: str):
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.author:
        return 403, None
    article.delete()
    return 204, None


@router.put("/articles/{slug}", auth=AuthJWT(), response={200: Any, 404: Any, 403: Any, 401: Any})
def update(request, slug: str, data: ArticlePartialUpdateSchema):
    """This is wrong, but this method behaves like a PATCH, as required by the RealWorld API spec"""
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    if request.user != article.author:
        return 403, None
    updated_fields = []
    for attr, value in data.article.dict(exclude_unset=True).items():
        setattr(article, attr, value)
        updated_fields.extend(["title", "slug"] if attr == "title" else [attr])
    article.save(update_fields=updated_fields)  # Prevents some race condition
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.get("/tags", response={200: Any})
def list_tags(request):
    return {"tags": [t.name for t in Tag.objects.all()]}
