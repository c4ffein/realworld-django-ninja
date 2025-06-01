from django.test import TestCase
from ninja.testing import TestClient

from image_server.api import router


class ImagesTestCase(TestCase):
    def setUp(self):
        self.client = TestClient(router)

    def test_images_get_png_ok(self):
        url = "/whatever.png"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content[:4], b"\x89\x50\x4e\x47")

    def test_images_get_jpg_ok(self):
        url = "/whatever.jpg"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content[:4], b"\xff\xd8\xff\xe0")

    def test_images_get_jpeg_ok(self):
        url = "/whatever.jpeg"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content[:4], b"\xff\xd8\xff\xe0")

    def test_images_get_unknown_ko(self):
        url = "/whatever.exe"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
