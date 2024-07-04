from typing import Any

from django.contrib.auth import authenticate
from django.conf import settings
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from ninja import Router
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken

from accounts.schemas import (
    EMPTY,
    ProfileSchema,
    UserCreateSchema,
    UserGetSchema,
    UserInPartialUpdateOutSchema,
    UserLoginSchema,
    UserMineSchema,
    UserPartialUpdateInSchema,
    UserPartialUpdateOutSchema,
)
from accounts.models import User
from helpers.auth import AuthJWT
from helpers.exceptions import clean_integrity_error
from django.conf import settings
from taggit.models import Tag
from ninja import Router

from accounts.models import User
from articles.models import Article
from articles.serializers import ArticleSerializer, TagSerializer
from articles.filters import ArticleFilter
from django.urls import path, include 
from rest_framework.routers import DefaultRouter
from articles.schemas import ArticleCreateSchema, ArticleOutSchema, ArticleUpdateSchema


router = Router()


@router.post('/articles/{slug}/favorite', auth=AuthJWT(), response={200: Any, 404: Any})
def favorite(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.favorites.filter(id=request.user.id).exists():
        return Response({"errors": {"body": ["Already Favourited Article"]}})
    article.favorites.add(request.user)
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.delete('/articles/{slug}/favorite', auth=AuthJWT(), response={200: Any, 404: Any})
def unfavorite(request, slug):
    article = get_object_or_404(Article, slug=slug)
    _ = get_object_or_404(article.favorites, id=request.user.id)
    article.favorites.remove(request.user.id)
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.get('/articles/feed', response={200: Any, 404: Any})
def feed(request):
    followed_authors = User.objects.filter(followers=request.user)
    articles = [a for a in Article.objects.filter(author__in=followed_authors).order_by('-created')]
    return {
        'articlesCount': len(articles),
        'articles': [ArticleOutSchema.from_orm(a, context={"request": request}) for a in articles],
    }


@router.get('/articles', response={200: Any})
def list_articles(request):
    return {"articles": [ArticleOutSchema.from_orm(a, context={"request": request}) for a in Article.objects.all()]}


@router.post('/articles', auth=AuthJWT(), response={201: Any, 422: Any})
def create_article(request, data: ArticleCreateSchema):
    article = Article.objects.create(**{**data.article.dict(), "author": request.user})
    return 201, {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.get('/articles/{slug}', response={200: Any, 404: Any})
def retrieve(request, slug: str):
    article = get_object_or_404(Article, slug=slug)
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.delete('/articles/{slug}', auth=AuthJWT(), response={200: Any, 404: Any, 403: Any, 401: Any})
def destroy(request, slug: str):
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.author:
        return 403, None
    article.delete()


@router.put('/articles/{slug}', auth=AuthJWT(), response={200: Any, 404: Any, 403: Any, 401: Any})
def update(request, slug: str, data: ArticleUpdateSchema):
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.author:
        return 403, None
    # Doing this to trigger slug-recalculation for now
    article.title = data.article.title
    article.summary = data.article.summary
    article.content = data.article.content
    article.save()
    return {"article": ArticleOutSchema.from_orm(article, context={"request": request})}


@router.get('/tags', response={200: Any})
def list_tags(request):
    return {"tags": [t.name for t in Tag.objects.all()]}
