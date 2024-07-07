from django.test import TestCase

from helpers.headered_client import HeaderedClient

from image_server.api import router

from config.urls import api


class ImagesTestCase(TestCase):
    def setUp(self):
        self.client = HeaderedClient(router)

    def test_images_get_png_ok(self):
        url = f'/whatever.png'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content[:4], b"\x89\x50\x4e\x47")

    def test_images_get_jpg_ok(self):
        url = f'/whatever.jpg'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content[:4], b"\xff\xd8\xff\xe0")

    def test_images_get_jpeg_ok(self):
        url = f'/whatever.jpeg'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content[:4], b"\xff\xd8\xff\xe0")

    def test_images_get_unknown_ko(self):
        url = f'/whatever.exe'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
