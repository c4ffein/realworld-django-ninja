from unittest import mock
import re
from json import loads

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import  AccessToken

from articles.models import Article
from articles.api import router
from helpers.headered_client import HeaderedClient


User = get_user_model() 


class ArticleViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@email.test', password='testpassword')
        access_token = self.access_token = str(AccessToken.for_user(self.user))
        self.client = HeaderedClient(
            router, headers={"Authorization": f"Token {access_token}", "Content-Type": "application/json"}
        )
        self.default_image = "https://api.realworld.io/images/smiley-cyrus.jpeg"
        self.article = Article.objects.create(
            author= self.user, 
            title="Test Title", 
            summary="Test summary",
            content="Test content",
            slug="test-slug",
        )
        self.other_user = User.objects.create_user(username='otheruser', email='e@g.c', password='whatever')
        self.other_article = Article.objects.create(
            author= self.other_user, 
            title="Other Test Title", 
            summary="Other Test summary",
            content="Other Test content",
            slug="other-test-slug",
        )
        self.other_article.tags.add("OT")
        self.other_user.followers.add(self.user)
        self.article_out = {
            'slug': 'test-title',
            'title': 'Test Title',
            'description': 'Test summary',
            'body': 'Test content',
            'tagList': [],
            'createdAt': mock.ANY,
            'updatedAt': mock.ANY,
            'favorited': False,
            'favoritesCount': 0,
            'author': {'username': 'testuser', 'bio': None, 'image': self.default_image, 'following': False},
        }
        self.other_article_out = {
            'slug': 'other-test-title',
            'title': 'Other Test Title',
            'description': 'Other Test summary',
            'body': 'Other Test content',
            'tagList': ["OT"],
            'createdAt': mock.ANY,
            'updatedAt': mock.ANY,
            'favorited': False,
            'favoritesCount': 0,
            'author': {'username': 'otheruser', 'bio': None, 'image': self.default_image, 'following': True},
        }

    def _valid_timestamps_in_output_dict(self, output_dict):
        ts_regex = r"\b[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]*Z\b"
        self.assertTrue(re.search(ts_regex, output_dict["createdAt"]))
        self.assertTrue(re.search(ts_regex, output_dict["updatedAt"]))

    def test_get_articles(self):
        response = self.client.get("/articles", user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("articles", None), [self.article_out, self.other_article_out])
        self._valid_timestamps_in_output_dict(response.data.get("articles", None)[0])
        self._valid_timestamps_in_output_dict(response.data.get("articles", None)[1])
        
    def test_get_article_feed(self):
        response = self.client.get("/articles/feed", user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'articlesCount': 1,
            'articles': [
                {
                    'slug': 'other-test-title',
                    'title': 'Other Test Title',
                    'description': 'Other Test summary',
                    'body': 'Other Test content',
                    'tagList': ["OT"],
                    'createdAt': mock.ANY,
                    'updatedAt': mock.ANY,
                    'favorited': False,
                    'favoritesCount': 0,
                    'author': {
                        'username': 'otheruser',
                        'bio': None,
                        'image': self.default_image,
                        'following': True,
                    },
                },
            ],
        })
        self._valid_timestamps_in_output_dict(loads(response.content)["articles"][0])
        
    def test_create_article(self):
        self.maxDiff = None
        new_article_data = {
            "article": {
                "title": "New Test Title",
                "description": "New Test Description",
                "body": "New Test Content",
                "tagList": ["tag", "taag", "taaag"]
            }
        }
        response = self.client.post("/articles", json=new_article_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {
            'article': {
                'slug': 'new-test-title',
                'title': 'New Test Title',
                'description': 'New Test Description',
                'body': 'New Test Content',
                'tagList': mock.ANY,
                'createdAt': mock.ANY,
                'updatedAt': mock.ANY,
                'favorited': False,
                'favoritesCount': 0,
                'author': {'username': 'testuser', 'bio': None, 'image': self.default_image, 'following': False},
            },
        })
        self._valid_timestamps_in_output_dict(response.data["article"])
        self.assertEqual(set(response.data["article"]["tagList"]), set(["tag", "taag", "taaag"])),
        self.assertEqual(Article.objects.count(), 3)
        self.assertEqual(Article.objects.values().last(), {
            'author_id': self.user.id,
            'content': 'New Test Content',
            'created': mock.ANY,
            'id': Article.objects.last().id,
            'slug': 'new-test-title',
            'summary': 'New Test Description',
            'title': 'New Test Title',
            'updated': mock.ANY, 
        })
    
    def test_create_article_invalid_data_missing_field(self):
        new_article_data = {
            "article": {
                "description": "New Test Description",
                "body": "New Test Content",
                "tagList": ["tag", "taag", "taaag"]
            }
        }
        response = self.client.post("/articles", json=new_article_data)
        self.assertEqual(response.status_code, 422)

    def test_create_article_additional_unused_field_still_ok(self):
        new_article_data = {
            "article": {
                "title": "New Test Title",
                "tatle": "New Test Tatle",
                "description": "New Test Description",
                "body": "New Test Content",
                "tagList": ["tag", "taag", "taaag"]
            }
        }
        response = self.client.post("/articles", json=new_article_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_article_invalid_data_incorrect_tag_list(self):
        new_article_data = {
            "article": {
                "title": "New Test Title",
                "description": "New Test Description",
                "body": "New Test Content",
                "tagList": "tag; taag; taaag"
            }
        }
        response = self.client.post("/articles", json=new_article_data)
        self.assertEqual(response.status_code, 422)
        
    def test_get_article(self):
        response = self.client.get(f"/articles/{self.article.slug}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"article": self.article_out})
        self._valid_timestamps_in_output_dict(response.data["article"])
        
    def test_update_article(self):
        self.maxDiff=None
        update_article_data = {
            "article": {
                "title": "New Test Title",
                "description": "New Test Description",
                "body": "New Test Content",
            }
        }
        response = self.client.put(f"/articles/{self.article.slug}", json=update_article_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'article': {
                **self.article_out,
                "tagList": mock.ANY,
                'slug': 'new-test-title',
                'title': 'New Test Title',
                'description': 'New Test Description',
                'body': 'New Test Content',
            },
        })
        self._valid_timestamps_in_output_dict(response.data["article"])
        self.assertEqual(set(response.data["article"]["tagList"]), set([])),
        self.assertEqual(Article.objects.values().filter(title="New Test Title").last(), {
            'author_id': self.user.id,
            'content': 'New Test Content',
            'created': mock.ANY,
            'id': self.article.id,
            'slug': 'new-test-title',
            'summary': 'New Test Description',
            'title': 'New Test Title',
            'updated': mock.ANY, 
        })
    
    def test_update_article_invalid_data_missing_field(self):
        update_article_data = {
            "article": {
                "description": "New Test Description",
                "body": "New Test Content",
                "tagList": ["tag", "taag", "taaag"]
            }
        }
        response = self.client.put(f"/articles/{self.article.slug}", json=update_article_data)
        self.assertEqual(response.status_code, 422)

    def test_update_article_invalid_data_additional_field_still_works(self):
        update_article_data = {
            "article": {
                "title": "New Test Title",
                "tatle": "New Test Tatle",
                "description": "New Test Description",
                "body": "New Test Content",
                "tagList": ["tag", "taag", "taaag"]
            }
        }
        response = self.client.put(f"/articles/{self.article.slug}", json=update_article_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_cant_update_article_without_being_logged(self):
        self.client.headers["Authorization"] = None
        update_article_data = {"article": {"title": "New Test Title"}}
        response = self.client.put(f"/articles/{self.article.slug}", json=update_article_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Article.objects.filter(title="New Test Title").count(), 0)

    def test_cant_update_article_of_another_user(self):
        update_article_data = {"article": {"title": "New Test Title", "description": "?", "body": "?"}}
        response = self.client.put(f"/articles/{self.other_article.slug}", json=update_article_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Article.objects.filter(title="New Test Title").count(), 0)
        
    def test_delete_article(self):
        response = self.client.delete(f"/articles/{self.article.slug}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Article.objects.count(), 1)
    
    def test_cant_delete_article_without_being_logged(self):
        self.client.headers["Authorization"] = None
        response = self.client.delete(f"/articles/{self.article.slug}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Article.objects.count(), 2)

    def test_cant_delete_article_of_another_user(self):
        response = self.client.delete(f"/articles/{self.other_article.slug}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Article.objects.count(), 2)
        
    def test_favorite_article(self):
        response = self.client.post(f"/articles/{self.article.slug}/favorite")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'article': {**self.article_out, 'favorited': True, 'favoritesCount': 1,}})
        self._valid_timestamps_in_output_dict(response.data["article"])
        self.assertEqual(self.article.favorites.count(), 1)

    def test_unfavorite_article(self):
        self.article.favorites.add(self.user)
        response = self.client.delete(f"/articles/{self.article.slug}/favorite")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"article": self.article_out})
        self._valid_timestamps_in_output_dict(response.data["article"])
        self.assertEqual(self.article.favorites.count(), 0)
        

class TagViewSet(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@email.test', password='testpassword')
        self.article = Article.objects.create(
            author= self.user, 
            title="Test Title", 
            summary="Test summary",
            content="Test content",
            slug="test-slug",
        )
        self.article.tags.add("red", "green", "blue")

    def test_list_tags(self):
        response = self.client.get("/api/tags")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = loads(response.content)
        self.assertEqual(data, {"tags": mock.ANY})
        self.assertEqual(set(data["tags"]), {"red", "green", "blue"})
