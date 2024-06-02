from unittest import mock
import re

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import  AccessToken

from articles.models import Article
from comments.models import Comment


User = get_user_model()


class CommentViewTestCase(APITestCase):
    def setUp(self):
        for i in range(2):
            user = User.objects.create_user(username=f"testuser{i}", password="pass", email=f"test{i}@email.email")
            setattr(self, f"user_{i}", user)
            setattr(
                self,
                f"article_{i}",
                Article.objects.create(
                    author = user,
                    title = f"Title {i}",
                    summary = f"Summary {i}",
                    content = f"Content {i}",
                    slug = f"test-slug-{i}",
                )
            )
        self.access_token = str(AccessToken.for_user(self.user_0))
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.access_token}")
        for i, article, author in [[0, self.article_0, self.user_1], [1, self.article_0, self.user_0]]:
            comment = Comment.objects.create(article = article, author = author, content = f"comment {i} content")
            setattr(self, f"comment_{i}", comment)
    
    def _valid_timestamps_in_output_dict(self, output_dict):
        ts_regex = r"\b[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]*Z\b"
        self.assertTrue(re.search(ts_regex, output_dict["createdAt"]))
        self.assertTrue(re.search(ts_regex, output_dict["updatedAt"]))    

    def test_get_comments_list_on_article_without_comment(self):
        url = f'/api/articles/{self.article_1.slug}/comments'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"comments": []})

    def test_get_comments_list_on_article_with_comments(self):
        url = f'/api/articles/{self.article_0.slug}/comments'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'comments': [
                    {
                        'id': comment.id,
                        'createdAt': mock.ANY,
                        'updatedAt': mock.ANY,
                        'body': f"comment {n} content",
                        'author': {'username': f"testuser{u}", 'bio': '', 'image': None, 'following': False},
                    } for comment, n, u in [[self.comment_1, 1, 0], [self.comment_0, 0, 1]]
                ],
            },
        )
        self._valid_timestamps_in_output_dict(response.data["comments"][0])
        self._valid_timestamps_in_output_dict(response.data["comments"][1])

    def test_create_comment(self):
        url = f'/api/articles/{self.article_1.slug}/comments'
        data = {'comment': {'body': 'This is a test comment'}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'comment': {
                    'id': self.article_1.comment_set.first().id,
                    'createdAt': mock.ANY,
                    'updatedAt': mock.ANY,
                    'body': 'This is a test comment',
                    'author': {'username': 'testuser0', 'bio': '', 'image': None, 'following': False},
                },
            },
        )
        self.assertEqual(self.article_1.comment_set.count(), 1)
        self.assertEqual(self.article_1.comment_set.first().content, "This is a test comment")
        self.assertEqual(self.article_1.comment_set.first().author, self.user_0)
        self._valid_timestamps_in_output_dict(response.data["comment"])

    def test_delete_comment(self):
        url = f'/api/articles/{self.article_0.slug}/comments/{self.comment_0.id}'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.article_0.comment_set.count(), 1)
        self.assertEqual(self.article_0.comment_set.first(), self.comment_1)
