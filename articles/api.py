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


router = Router()


## class ArticleView(viewsets.ModelViewSet):
##     queryset = Article.objects.all()
##     serializer_class = ArticleSerializer 
##     permission_classes=[IsAuthenticated]
##     lookup_field='slug'
##     filterset_class = ArticleFilter
##     http_method_names = ['get', 'post', 'put', 'delete']
##     
##     def get_permissions(self):
##         if self.action == 'retrieve' or self.action == 'list':
##             return [IsAuthenticatedOrReadOnly()]
## 
##         return super().get_permissions()
##     
##     
##     def create(self, request, *args, **kwargs):
##         try:
##             article_data = request.data.get('article')
##             serializer = self.get_serializer(data=article_data)
##             serializer.is_valid(raise_exception=True)
##             self.perform_create(serializer)
##             headers = self.get_success_headers(serializer.data)
##             return Response({"article":serializer.data}, status=status.HTTP_201_CREATED)
##         except Exception:
##             return Response({"errors": {"body": ["Bad Request"]}}, status=status.HTTP_404_NOT_FOUND)
##             
##     @action(detail=True, methods=['post', 'delete'])
##     def favorite(self, request, slug, *args, **kwargs):
##         if request.method == 'POST':
##             try:
##                 article = Article.objects.get(slug=slug)
##                 if article.favorites.filter(id=request.user.id).exists():
##                     return Response({"errors": {"body": ["Already Favourited Article"]}})
##                 article.favorites.add(request.user)
##                 serializer = self.get_serializer(article)
##                 return Response({"article": serializer.data})
##             except Exception:
##                 return Response({"errors": {"body": ["Bad Request"]}}, status=status.HTTP_404_NOT_FOUND)
##         else:
##             try:
##                 article = Article.objects.get(slug=slug)
##                 if article.favorites.get(id=request.user.id):
##                     article.favorites.remove(request.user.id)
##                     serializer = self.get_serializer(article)
##                     return Response({ "article": serializer.data })
##                 else:
##                     raise Exception
##             except Exception:
##                 return Response({"errors": {"body": ["Bad Request"]}}, status=status.HTTP_404_NOT_FOUND)
##             
##     @action(detail=False)
##     def feed(self, request, *args, **kwargs):
##         try:
##             followed_authors = User.objects.filter(followers=request.user)
##             queryset = self.get_queryset()
##             articles = [a for a in queryset.filter(author__in=followed_authors).order_by('-created')]
##             response = {
##                 'articlesCount': len(articles),
##                 'articles': [
##                     {
##                         "author": {
##                             "username": a.author.username,
##                             "bio": a.author.bio or None,
##                             "image": a.author.image or settings.DEFAULT_USER_IMAGE,
##                             "following": True,
##                         },
##                         "title": a.title,
##                         "description": a.summary,
##                         "body": a.content,
##                         "tagList": [t.name for t in a.tags.all()],
##                         'slug': a.slug,
##                         'createdAt': a.created,
##                         'updatedAt': a.updated,
##                         'favorited': bool(a.favorites.filter(id=request.user.id).count()),
##                         'favoritesCount': a.favorites.count(),
##                     }
##                     for a in articles
##                 ],
##             }
##             return Response(response)
##                
##         except Exception as e:
##             return Response({"errors": {"body": ["Bad Request"]}}, status=status.HTTP_404_NOT_FOUND)
##         
##     def retrieve(self, request, slug, *args, **kwargs):
##         try:
##             return Response({"article": self.get_serializer(self.get_queryset().get(slug=slug)).data})
##         except Exception:
##             return Response({"errors": {"body": ["Bad Request"]}}, status=status.HTTP_404_NOT_FOUND)
##     
##     def update(self, request, slug, *args, **kwargs):
##         try:
##             queryset = self.get_queryset()
##             article = queryset.get(slug=slug)
##             
##             if request.user != article.author:
##                 return Response({"errors": {"body": ["UnAuthorized Action"]}}, status=status.HTTP_401_UNAUTHORIZED)
##             request_data = request.data.get('article')
##             serializer = self.get_serializer(article, data=request_data)
##             serializer.is_valid(raise_exception=True)
##             self.perform_update(serializer)
##             return Response({"article": serializer.data})
##         
##         except Exception:
##             return Response({"errors": {"body": ["Bad Request"]}}, status=status.HTTP_404_NOT_FOUND)
##     
##     def destroy(self, request, slug, *args, **kwargs):
##         try:
##             article = self.get_queryset().get(slug=slug)
##             if request.user != article.author:
##                 return Response({"errors": {"body": ["UnAuthorized Action"]}}, status=status.HTTP_401_UNAUTHORIZED)
##             article.delete()
##             return Response(status=status.HTTP_200_OK)
##           
##         except Exception:
##             return Response({"errors": {"body": ["Bad Request"]}}, status=status.HTTP_404_NOT_FOUND)


@router.get('/tags', response={200: Any})
def list_tags(request):
    return {"tags": [t for t in Tag.objects.all()]}
