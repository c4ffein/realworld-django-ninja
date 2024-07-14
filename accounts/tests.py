from json import loads
from unittest import mock

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction
from django.test import TestCase
from parameterized import parameterized
from ninja_jwt.tokens import AccessToken

from accounts.api import router
from helpers.headered_client import HeaderedClient


User = get_user_model()


class AccountRegistrationTestCase(TestCase):
    def setUp(self):
        self.url = "users"
        self.base_user = {"email": "test@example.com", "password": "testpassword", "username": "testuser"}
        self.client = HeaderedClient(router, headers={"Content-Type": "application/json"})

    def test_account_registration(self):
        response = self.client.post(self.url, json={"user": self.base_user})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            loads(response.content),
            {
                "user": {
                    "username": "testuser",
                    "email": "test@example.com",
                    "bio": None,
                    "image": settings.DEFAULT_USER_IMAGE,
                    "token": mock.ANY,
                },
            },
        )
        self.assertEqual(sum(1 for c in loads(response.content)["user"]["token"] if c == "."), 2)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(
            User.objects.values().last(),
            {
                "bio": "",
                "date_joined": mock.ANY,
                "email": "test@example.com",
                "id": mock.ANY,
                "image": None,
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
                "last_login": None,
                "password": mock.ANY,
                "username": "testuser",
            },
        )
        self.assertIn("pbkdf2_sha256", User.objects.last().password)

    def test_account_registration_email_already_exists(self):
        response = self.client.post(self.url, json={"user": self.base_user})
        self.assertEqual(response.status_code, 201)
        with transaction.atomic():
            response = self.client.post(self.url, json={"user": {**self.base_user, "username": "gg"}})
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(loads(response.content), {"already_existing": "email"})

    def test_account_registration_username_already_exists(self):
        response = self.client.post(self.url, json={"user": self.base_user})
        self.assertEqual(response.status_code, 201)
        with transaction.atomic():
            response = self.client.post(self.url, json={"user": {**self.base_user, "email": "gg@example.com"}})
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(loads(response.content), {"already_existing": "username"})

    def test_account_registration_invalid_data_wrong_email(self):
        response = self.client.post(self.url, json={**self.base_user, "email": "no-at"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(User.objects.count(), 0)

    def test_account_registration_invalid_data_missing_keys(self):
        response = self.client.post(self.url, json={"user": {}})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(User.objects.count(), 0)

    def test_account_registration_invalid_data_missing_root_key(self):
        response = self.client.post(self.url, json={})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(User.objects.count(), 0)

    def test_account_registration_invalid_data_empty_fields(self):
        for replaced in ["email", "password", "username"]:
            response = self.client.post(self.url, json={"user": {**self.base_user, replaced: ""}})
            self.assertEqual(response.status_code, 422)
            self.assertEqual(User.objects.count(), 0)
            if replaced in ["password", "username"]:
                self.assertEqual(
                    loads(response.content),
                    {
                        "detail": [
                            {
                                "ctx": {"error": "can't be blank"},
                                "loc": ["body", "data", "user", replaced],
                                "msg": "Value error, can't be blank",
                                "type": "value_error",
                            },
                        ],
                    },
                )


class AccountLoginTestCase(TestCase):
    def setUp(self):
        self.email, self.username, self.password = "test@example.com", "testuser", "testpassword"
        self.user = User.objects.create_user(email=self.email, username=self.username, password=self.password)
        self.url = "users/login"
        self.client = HeaderedClient(router, headers={"Content-Type": "application/json"})

    def test_account_login(self):
        user_data = {"user": {"email": self.email, "password": self.password}}
        response = self.client.post(self.url, json=user_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            loads(response.content),
            {
                "user": {
                    "username": "testuser",
                    "email": "test@example.com",
                    "bio": None,
                    "image": settings.DEFAULT_USER_IMAGE,
                    "token": mock.ANY,
                },
            },
        )
        self.assertEqual(sum(1 for c in loads(response.content)["user"]["token"] if c == "."), 2)

    def test_account_login_bad_password(self):
        user_data = {"user": {"email": self.email, "password": "fail"}}
        response = self.client.post(self.url, json=user_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(loads(response.content), {"detail": [{"msg": "incorrect credentials"}]})

    def test_account_login_no_password(self):
        user_data = {"user": {"email": self.email}}
        response = self.client.post(self.url, json=user_data)
        self.assertEqual(response.status_code, 422)
        missing_password = {"type": "missing", "loc": ["body", "data", "user", "password"], "msg": "Field required"}
        self.assertEqual(loads(response.content), {"detail": [missing_password]})

    def test_account_login_invalid_data(self):
        invalid_user_data = {"user": {}}
        response = self.client.post(self.url, json=invalid_user_data)
        self.assertEqual(response.status_code, 422)
        missing_email = {"type": "missing", "loc": ["body", "data", "user", "email"], "msg": "Field required"}
        missing_password = {"type": "missing", "loc": ["body", "data", "user", "password"], "msg": "Field required"}
        self.assertEqual(loads(response.content), {"detail": [missing_email, missing_password]})


class UserViewTestCase(TestCase):
    def setUp(self):
        self.email, self.username, self.password = "test@example.com", "testuser", "testpassword"
        self.user = User.objects.create_user(email=self.email, username=self.username, password=self.password)
        self.access_token = str(AccessToken.for_user(self.user))
        self.client = HeaderedClient(
            router, headers={"Authorization": f"Token {self.access_token}", "Content-Type": "application/json"}
        )
        self.url = "user"
        self.base_update = {
            "email": "updated@example.com",
            "bio": "Updated bio",
            "image": "http://example.com/updated-image.jpg",
            "username": "UpdatedUsername",
        }
        self.default_user_statuses = {"is_active": True, "is_staff": False, "is_superuser": False}

    def test_user_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            loads(response.content),
            {"user": {"username": self.username, "email": self.email, "bio": "", "image": None}},
        )

    def test_user_view_get_not_logged(self):
        self.client.headers = {"Content-Type": "application/json"}
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(loads(response.content), {"detail": "Unauthorized"})

    @parameterized.expand([([bool((i >> j) % 2) for j in range(3, -1, -1)],) for i in range(0b10000)])
    def test_user_view_put(self, bools):
        """This is wrong, but this method behaves like a PATCH, as required by the RealWorld API spec"""
        filtered_update = {k: v for i, (k, v) in enumerate(self.base_update.items()) if bools[i]}
        response = self.client.put(self.url, json={"user": filtered_update})
        saved_user_value = {"email": "test@example.com", "username": "testuser", "bio": "", "image": None}
        base_values = {"id": self.user.id, "last_login": None, "date_joined": mock.ANY, "password": mock.ANY}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), {"user": {**saved_user_value, **filtered_update, "token": mock.ANY}})
        self.assertEqual(sum(1 for c in loads(response.content)["user"]["token"] if c == "."), 2)
        self.assertEqual(
            User.objects.values().last(),
            {**base_values, **self.default_user_statuses, **saved_user_value, **filtered_update},
        )

    def test_user_view_put_password(self):
        """This is wrong, but this method behaves like a PATCH, as required by the RealWorld API spec"""
        response = self.client.put(self.url, json={"user": {"password": "new_pass"}})
        saved_user_value = {"email": "test@example.com", "username": "testuser", "bio": "", "image": None}
        base_values = {"id": self.user.id, "last_login": None, "date_joined": mock.ANY, "password": mock.ANY}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), {"user": {**saved_user_value, "token": mock.ANY}})
        self.assertEqual(sum(1 for c in loads(response.content)["user"]["token"] if c == "."), 2)
        self.assertEqual(
            User.objects.values().last(),
            {**base_values, **self.default_user_statuses, **saved_user_value},
        )
        self.assertTrue(User.objects.last().check_password("new_pass"))

    def test_user_view_put_invalid_data_missing_key(self):
        """This is wrong, but this method behaves like a PATCH, as required by the RealWorld API spec"""
        response = self.client.put(self.url, json={})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            loads(response.content),
            {
                "detail": [
                    {"loc": ["body", "data", "user"], "msg": "Field required", "type": "missing"},
                ],
            },
        )

    def test_user_view_put_invalid_data_additional_key(self):
        """This is wrong, but this method behaves like a PATCH, as required by the RealWorld API spec"""
        response = self.client.put(self.url, json={"user": {**self.base_update}, "useer": []})
        self.assertEqual(response.status_code, 200)

    # TODO : At least one key for user
    # def test_user_view_put_invalid_data_no_dict(self):
    #     """This is wrong, but this method behaves like a PATCH, as required by the RealWorld API spec"""
    #     response = self.client.put(self.url, json={"user": ["aaa"]})
    #     self.assertEqual(response.status_code, 422)

    # TODO : At least one key for user
    # def test_user_view_put_invalid_data_missing_one_user_key(self):
    #     """This is wrong, but this method behaves like a PATCH, as required by the RealWorld API spec"""
    #     for key in ["email", "bio", "image", "username"]:
    #         response = self.client.put(self.url, json={"user": {}})
    #         self.assertEqual(response.status_code, 422)

    def test_user_view_put_invalid_data_wrong_mail_domain(self):
        """This is wrong, but this method behaves like a PATCH, as required by the RealWorld API spec"""
        response = self.client.put(self.url, json={"user": {**self.base_update, "email": "updated@exalom"}})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            loads(response.content),
            {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "data", "user", "email"],
                        "msg": (
                            "value is not a valid email address: The part after the @-sign is not valid. "
                            "It should have a period."
                        ),
                        "ctx": {"reason": "The part after the @-sign is not valid. It should have a period."},
                    },
                ],
            },
        )

    def test_user_view_put_invalid_data_wrong_mail(self):
        """This is wrong, but this method behaves like a PATCH, as required by the RealWorld API spec"""
        response = self.client.put(self.url, json={"user": {**self.base_update, "email": "updatexalom"}})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            loads(response.content),
            {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "data", "user", "email"],
                        "msg": (
                            "value is not a valid email address: The email address is not valid. "
                            "It must have exactly one @-sign."
                        ),
                        "ctx": {"reason": "The email address is not valid. It must have exactly one @-sign."},
                    },
                ],
            },
        )

    def test_user_view_put_not_logged(self):
        self.client.headers = {"Content-Type": "application/json"}
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(loads(response.content), {"detail": "Unauthorized"})


class ProfileDetailViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(email="test2@gmail.com", username="test2user", password="password")
        self.access_token = str(AccessToken.for_user(self.user))
        self.client = HeaderedClient(
            router, headers={"Authorization": f"Token {self.access_token}", "Content-Type": "application/json"}
        )
        self.url = f"/profiles/{self.user.username}"
        self.other_url = f"/profiles/{self.other_user.username}"
        self.dict = {"username": "testuser", "bio": None, "image": settings.DEFAULT_USER_IMAGE, "following": False}
        self.other_dict = {**self.dict, "username": "test2user"}

    def test_profile_detail_view_get_self(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), {"profile": self.dict})

    def test_profile_detail_view_get_without_login(self):
        self.client.headers = {"Content-Type": "application/json"}
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), {"profile": self.dict})

    def test_profile_detail_view_get_other_not_followed(self):
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), {"profile": self.other_dict})

    def test_profile_detail_view_get_other_followed(self):
        self.other_user.followers.add(self.user)
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), {"profile": {**self.other_dict, "following": True}})

    def test_profile_detail_view_follow(self):
        response = self.client.post(f"{self.other_url}/follow")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), {"profile": {**self.other_dict, "following": True}})
        self.assertEqual(self.other_user.followers.count(), 1)
        self.assertEqual(self.other_user.followers.last().id, self.user.id)

    def test_profile_detail_view_unfollow(self):
        self.other_user.followers.add(self.user)
        response = self.client.delete(f"{self.other_url}/follow")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), {"profile": self.other_dict})
        self.assertEqual(self.other_user.followers.count(), 0)

    def test_profile_detail_view_cant_unfollow_if_not_logged(self):
        self.client.headers = {"Content-Type": "application/json"}
        response = self.client.delete(f"{self.other_url}/follow")
        self.assertEqual(response.status_code, 401)

    def test_profile_detail_view_cant_unfollow_not_followed(self):
        response = self.client.delete(f"{self.other_url}/follow")
        self.assertEqual(response.status_code, 400)  # TODO Better 409

    def test_profile_detail_view_cant_follow_yourself(self):
        response = self.client.post(f"/profiles/{self.user.username}/follow")
        self.assertEqual(response.status_code, 400)  # TODO Better 409

    def test_profile_detail_view_cant_follow_nonexistent(self):
        response = self.client.post("/profiles/9000/follow")
        self.assertEqual(response.status_code, 404)

    # TODO Exception with this new router as it cannot resolve obviously, decide if delete
    # def test_profile_detail_view_cant_follow_wrong_path(self):
    #     response = self.client.post(f"/profiles/{self.user.username}/follow/23")
    #     self.assertEqual(response.status_code, 404)
