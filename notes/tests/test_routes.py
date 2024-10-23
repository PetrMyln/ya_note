from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователей.
        cls.author = User.objects.create(username='testUser')
        cls.reader = User.objects.create(username='testReader')
        cls.user_client = Client()
        # создаём заметку
        cls.note = Note.objects.create(
            title='testtitle',
            text='testtext',
            slug='testslug',
            author=cls.author)

    def test_pages_availability_for_anonymous_user(self):
        """
        Тестирование страниц для анонимных пользователей
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """
        Тестирование страниц для авторезированных пользователей
        """
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                self.client.force_login(self.reader)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """
        Тестирование редактирования страниц
        для авторезированных пользователей,
        которые не авторы заметок
        """
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        self.client.force_login(self.reader)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):

        """
        Тестирование редиректа для авторезированных
        и не авторезирвоанных пользователей
        """

        url_list = (('notes:edit', (self.note.slug,)),
                    ('notes:delete', (self.note.slug,)),
                    ('notes:detail', (self.note.slug,)),
                    ('notes:add', None),
                    ('notes:list', None),
                    ('notes:success', None),
                    )
        login_url = reverse('users:login')
        for name, slug in url_list:
            with self.subTest(name=name):
                url = reverse(name, args=slug)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
