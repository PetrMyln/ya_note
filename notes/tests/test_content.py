# news/tests/test_content.py
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class eTestHomePage(TestCase):
    NOTES_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        # Вычисляем текущую дату.

        cls.author = User.objects.create(username='testUser')
        # cls.client.force_login(cls.author)
        # print(cls.author.id)
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                # Для каждой новости уменьшаем дату на index дней от today,
                # где index - счётчик цикла.
                slug=index,
                author=cls.author
            )
            for index in range(1, 21)
        ]
        Note.objects.bulk_create(all_notes)

    def del_test_notes_count(self):
        # Загружаем главную страницу.
        response = self.client.get(self.NOTES_LIST_URL)
        # Код ответа не проверяем, его уже проверили в тестах маршрутов.
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем количество записей в списке.
        news_count = object_list.count()
        # Проверяем, что на странице именно 10 новостей.
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']
        # Получаем даты новостей в том порядке, как они выведены на странице.
        all_notes = [note.pk for note in object_list]
        # Сортируем полученный список по убыванию.
        sorted_dates = sorted(all_notes)
        # print(all_notes)
        # print(sorted_dates)
        # Проверяем, что исходный список был отсортирован правильно.
        self.assertEqual(all_notes, sorted_dates)


class eTestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='testUser')
        cls.note = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            slug='test',
            author=cls.author
        )

        cls.detail_url = reverse(
            'notes:edit', args=(cls.note.slug,))
        print(cls.detail_url)

    def del_test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)


class TestNotesInList(TestCase):
    NOTES_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author_one = User.objects.create(username='testUser1')
        cls.author_two = User.objects.create(username='testUser2')
        cls.note_one = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            slug='test',
            author=cls.author_one
        )

    def test_notes_list_for_different_users(self):
        users_and_rule_for_note = (
            (self.author_one, True),
            (self.author_two, False),
        )
        for user, rule in users_and_rule_for_note:
            self.client.force_login(user)
            response = self.client.get(self.NOTES_LIST_URL)
            object_list = response.context['object_list']
            assert (self.note_one in object_list) is rule
            self.client.logout()

    def test_pages_contains_form(self):
        urls_and_slug = (
            ('notes:add', None),
            ('notes:edit', (self.note_one.slug,)),
        )
        self.client.force_login(self.author_one)
        for name, slug in urls_and_slug:
            with self.subTest(name=name):
                url = reverse(name, args=slug)
                response = self.client.get(url)
                assert 'form' in response.context
                assert isinstance(response.context['form'], NoteForm)