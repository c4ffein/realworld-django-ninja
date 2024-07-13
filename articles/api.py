from typing import Any

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from ninja import Router

from accounts.models import User
from helpers.auth import AuthJWT
from helpers.exceptions import clean_integrity_error
from taggit.models import Tag

from articles.models import Article
from articles.schemas import ArticleCreateSchema, ArticleOutSchema, ArticlePartialUpdateSchema, EMPTY


router = Router()


@router.post("/articles/{slug}/favorite", auth=AuthJWT(), response={200: Any, 404: Any})
def favorite(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.favorites.filter(id=request.user.id).exists():
        return 409, {"errors": {"body": ["Already Favourited Article"]}}
    article.favorites.add(request.user)
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.delete("/articles/{slug}/favorite", auth=AuthJWT(), response={200: Any, 404: Any})
def unfavorite(request, slug):
    article = get_object_or_404(Article, slug=slug)
    get_object_or_404(article.favorites, id=request.user.id)
    article.favorites.remove(request.user.id)
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.get("/articles/feed", auth=AuthJWT(), response={200: Any, 404: Any})
def feed(request):
    followed_authors = User.objects.filter(followers=request.user)
    articles = [a for a in Article.objects.filter(author__in=followed_authors).order_by("-created")]
    return {
        "articlesCount": len(articles),
        "articles": [ArticleOutSchema.from_orm(a, context={"request": request}) for a in articles],
    }


@router.get("/articles", response={200: Any})
def list_articles(request):
    return {"articles": [ArticleOutSchema.from_orm(a, context={"request": request}) for a in Article.objects.all()]}


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
    return 201, {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.get("/articles/{slug}", auth=AuthJWT(pass_even=True), response={200: Any, 404: Any})
def retrieve(request, slug: str):
    article = get_object_or_404(Article, slug=slug)
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
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.author:
        return 403, None
    # Doing this to trigger slug-recalculation for now
    article.title = data.article.title if data.article.title != EMPTY else article.title
    article.summary = data.article.summary if data.article.summary != EMPTY else article.summary
    article.content = data.article.content if data.article.content != EMPTY else article.content
    article.save()
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.get("/tags", response={200: Any})
def list_tags(request):
    return {"tags": [t.name for t in Tag.objects.all()]}
