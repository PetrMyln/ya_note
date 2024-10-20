from http import HTTPStatus

from django.contrib.auth import get_user_model

from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):
    # сценарии для анонимных пользователей поиск по яндексу
    # типо проверка если удалать классметод то проверяем страницы на доспуность не залогиненого пользователя
    @classmethod
    def setUpTestData(cls):
        # Создаём пользователя.
        cls.author = User.objects.create(username='testUser')
        cls.reader = User.objects.create(username='Читатель простой')
        # создаём заметку
        cls.note = Note.objects.create(
            title='Заголовок',
            text='wzp',
            slug='wzzzup',
            author=cls.author)
        # не авторизированный пользователь
        cls.unlogin_user = Client().logout()
        cls.user_client = Client()
        # логинимся
        #cls.user_client.force_login(cls.user)
    def test_availability_for_notes_crud(self):
        """
            Проверка на удаление, добавление,просмотр и редактирвоание заметки
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.FOUND),
            (self.unlogin_user, HTTPStatus.FOUND),
            (self.user_client, HTTPStatus.FOUND),
        )
        url_list = (('notes:edit', self.note.slug),
                    ('notes:delete', self.note.slug),
                    ('notes:detail', self.note.slug),
                    ('notes:add', None),
                    ('notes:list', None),
                    ('notes:success', None),
                    )
        for user, status in users_statuses:
            if status == HTTPStatus.OK:
                self.client.force_login(user)
            for name, slug in url_list:
                with self.subTest(user=user, name=name):
                    if slug is not None:
                        url = reverse(name, args=(slug,))
                    else:
                        url = reverse(name)
                    response = self.client.get(url)
                    #print(url)
                    #print(response.status_code, status, ' thiiiiis')
                    self.assertEqual(response.status_code, status)
                    #self.client.logout(user)
            self.client.logout()
    def test_redirect_for_anonymous_client(self):

        # Сохраняем адрес страницы логина:

        url_list = (('notes:edit', self.note.slug),
                    ('notes:delete', self.note.slug),
                    ('notes:detail', self.note.slug),
                    ('notes:add', None),
                    ('notes:list', None),
                    ('notes:success', None),
                    )
        login_url = reverse('users:login')
        for name, slug in url_list:
            with self.subTest(name=name):
                if slug is None:
                    url = reverse(name)
                else:
                    url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_availability(self):
        """
        тестирование страниц для доступа
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


