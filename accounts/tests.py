from unittest import mock

from django.contrib.auth import get_user_model
from django.urls import reverse 
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import  AccessToken

# from accounts.models import User
User = get_user_model()


class AccountRegistrationTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/users"
        self.base_user = {'email': 'test@example.com', 'password': 'testpassword', 'username': 'testuser'}

    def test_account_registration(self):
        response = self.client.post(self.url, {'user': self.base_user}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(
            User.objects.values().last(),
            {
                'bio': '',
                'date_joined': mock.ANY,
                'email': 'test@example.com',
                'id': mock.ANY,
                'image': None,
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
                'last_login': None,
                'password': mock.ANY,
                'username': 'testuser',
            }
        )
        self.assertIn("pbkdf2_sha256", User.objects.last().password)

    def test_account_registration_invalid_data_wrong_email(self):
        response = self.client.post(self.url, {**self.base_user, "email": "no-at"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_account_registration_invalid_data_missing_keys(self):
        response = self.client.post(self.url, {'user': { }}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    # TODO Better
    # def test_account_registration_invalid_data_additional_keys(self):
    #     response = self.client.post(self.url, {'user': {**self.base_user, "hack": "the_gibson"}}, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(User.objects.count(), 0)

    def test_account_registration_invalid_data_missing_root_key(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    # TODO Better
    # def test_account_registration_invalid_data_additional_root_key(self):
    #     response = self.client.post(self.url, {'user': self.base_user, "hack": "the_gibson"}, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(User.objects.count(), 0)
   
    
class AccountLoginTestCase(APITestCase):
    def setUp(self):
        self.email, self.username, self.password = 'test@example.com', 'testuser', 'testpassword'
        self.user = User.objects.create_user(email=self.email, username=self.username, password=self.password)
        self.url = '/api/users/login'
        
    def test_account_login(self):
        user_data = {'user': { 'email': self.email, 'password': self.password}}
        response = self.client.post(self.url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            response.data, {
                'user': {
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'bio': '',
                    'image': None,
                    'token': mock.ANY,
                },
            }
        )
        self.assertEqual(sum(1 for c in response.data["user"]["token"] if c == "."), 2)

    def test_account_login_bad_password(self):
        user_data = {'user': { 'email': self.email, "password": "fail"}}
        response = self.client.post(self.url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # TODO Better 401 instead
        self.assertEqual(response.data, None)  # TODO Better

    def test_account_login_no_password(self):
        user_data = {'user': { 'email': self.email}}
        response = self.client.post(self.url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, None)  # TODO Better
        
    def test_account_login_invalid_data(self):
        invalid_user_data = {'user': { }}
        response = self.client.post(self.url, invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, None)  # TODO Better


class UserViewTestCase(APITestCase):
    def setUp(self):
        self.email, self.username, self.password = 'test@example.com', 'testuser', 'testpassword'
        self.user = User.objects.create_user(email=self.email, username=self.username, password=self.password)
        self.access_token = str(AccessToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.access_token)
        self.url = reverse('user-account')
        self.base_update = {
            "email": "updated@example.com",
            "bio": 'Updated bio',
            "image": 'http://example.com/updated-image.jpg',
        }
        self.default_user_statuses = {'is_active': True, 'is_staff': False, 'is_superuser': False}

    def test_user_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'username': self.username, 'email': self.email, 'bio': '', 'image': None})
        
    def test_user_view_put(self):
        response = self.client.put(self.url, {"user": self.base_update}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  
        self.assertEqual(response.data, {'username': self.username, **self.base_update})
        self.assertEqual(User.objects.values().last(), {
            'date_joined': mock.ANY,
            'id': self.user.id,
            'last_login': None,
            'password': mock.ANY,
            'username': self.username,
            **self.default_user_statuses,
            **self.base_update,
        })

    # TODO Better
    # def test_user_view_put_invalid_data_missing_key(self):
    #     response = self.client.put(self.url, {}, format='json')

    def test_user_view_put_invalid_data_additional_key(self):
        response = self.client.put(self.url, {"user": {**self.base_update}, "useer": []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # TODO Better

    # TODO Better
    # def test_user_view_put_invalid_data_no_dict(self):
    #     response = self.client.put(self.url, {"user": ["aaa"]}, format='json')

    def test_user_view_put_invalid_data_wrong_mail_domain(self):
        response = self.client.put(self.url, {"user": {**self.base_update, "email": "updated@exalom"}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # TODO Better

    def test_user_view_put_invalid_data_wrong_mail(self):
        response = self.client.put(self.url, {"user": {**self.base_update, "email": "updatexalom"}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # TODO Better

    def test_user_view_put_invalid_data_image_link(self):
        response = self.client.put(self.url, {"user": {**self.base_update, "image": "image.exe"}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # TODO Better
        
        
class ProfileDetailViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', username='testuser', password='testpassword')
        self.other_user = User.objects.create_user(email='test2@gmail.com', username='test2user', password='password')
        self.access_token = str(AccessToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.access_token}")
        self.url = f"/api/profiles/{self.user.username}"
        self.other_url = f"/api/profiles/{self.other_user.username}"
        self.dict = {'username': 'testuser', 'bio': '', 'image': None, 'following': False}
        self.other_dict = {'username': 'test2user', 'bio': '', 'image': None, 'following': False}

    def test_profile_detail_view_get_self(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.dict)

    def test_profile_detail_view_get_other_not_followed(self):
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.other_dict)

    def test_profile_detail_view_get_other_followed(self):
        self.other_user.followers.add(self.user)
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {**self.other_dict, 'following': True})
        
    def test_profile_detail_view_follow(self):
        response = self.client.post(f'{self.other_url}/follow')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'profile': {**self.other_dict, 'following': True}})
        self.assertEqual(self.other_user.followers.count(), 1)
        self.assertEqual(self.other_user.followers.last().id, self.user.id)

    def test_profile_detail_view_unfollow(self):
        self.other_user.followers.add(self.user)
        response = self.client.delete(f'{self.other_url}/follow')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'profile': self.other_dict})
        self.assertEqual(self.other_user.followers.count(), 0)

    def test_profile_detail_view_cant_unfollow_not_followed(self):
        response = self.client.delete(f'{self.other_url}/follow')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # TODO Better 409

    def test_profile_detail_view_cant_follow_yourself(self):
        response = self.client.post(f'/api/profiles/{self.user.username}/follow')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # TODO Better 409
    
    def test_profile_detail_view_cant_follow_nonexistent(self):
        response = self.client.post(f'/api/profiles/9000/follow')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_profile_detail_view_cant_follow_wrong_path(self):
        response = self.client.post(f'/api/profiles/{self.user.username}/follow/23')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
