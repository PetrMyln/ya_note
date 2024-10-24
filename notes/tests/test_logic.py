from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from pytils.translit import slugify

from notes.models import Note
from notes.tests.conftest import (
    User,
    FORM_DATA,
)


class TestLogicToCreateNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователей.
        cls.author = User.objects.create(username='testUser')
        cls.reader = User.objects.create(username='testReader')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_user_can_create_note(self):
        response = self.url_and_response(
            'notes:add',
            self.author_client,
            FORM_DATA,
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, FORM_DATA['title'])
        self.assertEqual(new_note.text, FORM_DATA['text'])
        self.assertEqual(new_note.slug, FORM_DATA['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.url_and_response(
            'notes:add',
            self.client,
            FORM_DATA,
        )
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={reverse("notes:add")}'
        self.assertRedirects(response, expected_url)
        assert Note.objects.count() == 0

    def test_empty_slug(self):
        slug = FORM_DATA.pop('slug')
        response = self.url_and_response(
            'notes:add',
            self.author_client,
            FORM_DATA,
        )
        self.assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        expected_slug = slugify(FORM_DATA['title'])
        self.assertEqual(new_note.slug, expected_slug)
        FORM_DATA['slug'] = slug

    def url_and_response(self,
                         viewname,
                         this_author,
                         data=FORM_DATA):
        url = reverse(viewname=viewname)
        return this_author.post(url, data)


class TestLogicEditSlug(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='testUser')
        cls.reader = User.objects.create(username='testReader')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='testtitle',
            text='testtext',
            slug='testslug',
            author=cls.author)

    def test_author_can_edit_note(self):
        response = self.url_and_response(
            'notes:edit',
            self.note.slug,
            self.author_client,
            FORM_DATA)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, FORM_DATA['title'])
        self.assertEqual(self.note.text, FORM_DATA['text'])
        self.assertEqual(self.note.slug, FORM_DATA['slug'])

    def test_other_user_cant_edit_note(self):
        response = self.url_and_response(
            'notes:edit',
            self.note.slug,
            self.not_author_client,
            FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        response = self.url_and_response(
            'notes:delete',
            self.note.slug,
            self.author_client)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        response = self.url_and_response(
            'notes:delete',
            self.note.slug,
            self.not_author_client)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def url_and_response(self,
                         viewname,
                         args,
                         this_author,
                         data=None):
        url = reverse(viewname=viewname, args=(args,))
        return this_author.post(url, data)
