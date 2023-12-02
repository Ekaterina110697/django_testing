from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestRoutes(TestCase):
    TITLE_TEXT = 'Новый заголовок'
    COMMENT_TEXT = 'Текст комментария'
    SLUG_TEXT = 'slug_text'
    TITLE = 'Title'
    TEXT = 'TEXT'
    SLUG = 'SLug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': cls.TITLE_TEXT,
            'text': cls.COMMENT_TEXT,
            'slug': cls.SLUG_TEXT,
        }
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )
        cls.add_url = reverse('notes:add')
        cls.add_success = reverse('notes:success')
        cls.add_url_2 = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_anonymous_user_cant_create_note(self):
        """Проверка что анонимный пользователь не может создавать заметки"""
        note_count = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), note_count)

    def test_user_can_create_note(self):
        """Авторизированный пользователь может создавать заметки"""
        Note.objects.all().delete()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.add_success)
        self.assertEqual(Note.objects.count(), 1)
        notes = Note.objects.get()
        self.assertEqual(notes.title, self.TITLE_TEXT)
        self.assertEqual(notes.text, self.COMMENT_TEXT)
        self.assertEqual(notes.slug, self.SLUG_TEXT)
        self.assertEqual(notes.author, self.author)

    def test_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug"""
        note_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        self.author_client.post(self.add_url, data=self.form_data)
        response = self.author_client.post(self.add_url, data=self.form_data)
        warning = self.form_data['slug'] + WARNING
        self.assertFormError(response, form='form',
                             field='slug', errors=warning)
        self.assertEqual(Note.objects.count(), note_count)

    def test_auto_slug(self):
        """Автоматически формируется slug"""
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.add_success)
        self.assertEqual(Note.objects.count(), 1)
        note_slug = Note.objects.get()
        slugify_slug = slugify(self.form_data['title'])
        self.assertEqual(note_slug.slug, slugify_slug)

    def test_anonymous_user_cant_delete_note(self):
        """Не зарегистрированный пользователь не может удалять заметки"""
        note_count = Note.objects.count()
        response = self.reader_client.post(
            self.add_url_2,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), note_count)

    def test_author_can_delete_note(self):
        """Может удалять заметки"""
        note_count = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), note_count - 1)

    def test_author_can_edit_note(self):
        """Может править свои заметки"""
        self.author_client.post(self.add_url_2, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE_TEXT)
        self.assertEqual(self.note.text, self.COMMENT_TEXT)
        self.assertEqual(self.note.slug, self.SLUG_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Не может править чужие заметки"""
        response = self.reader_client.post(self.add_url_2, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        note_slug_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.text, note_slug_db.text)
        self.assertEqual(self.note.title, note_slug_db.title)
        self.assertEqual(self.note.slug, note_slug_db.slug)

    def test_reader_cant_delete_user_note(self):
        """Пользователь не может удалять чужие заметки"""
        response = self.reader_client.delete(self.delete_url)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)
