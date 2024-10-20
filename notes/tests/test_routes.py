from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from notes.models import Note

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = Note.objects.create(title='Заголовок', text='Текст')

    def test_home_page(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

