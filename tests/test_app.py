import unittest
from app import app

class TestURLShortener(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_shorten_url(self):
        response = self.app.post('/', data={'long_url': 'https://example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Shortened URL:', response.data)