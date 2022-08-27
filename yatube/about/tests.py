from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase


class TestUrlAbout(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.url_templates = {
            reverse("about:author"): "about/author.html",
            reverse("about:tech"): "about/tech.html",
        }

    def test_url_status_codes(self):
        for url in self.url_templates.keys():
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_templates_used(self):
        for url, template in self.url_templates.items():
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertTemplateUsed(response, template)
