from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note
from notes.tests.conftest import (
    User,
)


class TestNotesInList(TestCase):
    """
    Тест
    - в список заметок одного пользователя
        не попадают заметки другого пользователя;
    - на страницы создания и редактирования заметки передаются формы.
    """
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
