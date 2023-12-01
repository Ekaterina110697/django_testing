from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author)
        cls.home_url = reverse('notes:home', None)
        cls.login_url = reverse('users:login', None)
        cls.logout_url = reverse('users:logout', None)
        cls.signup_url = reverse('users:signup', None)
        cls.add_url = reverse('notes:add', None)
        cls.list_url = reverse('notes:list', None)
        cls.success_url = reverse('notes:success', None)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_pages_availability_for_anonym_user(self):
        urls = (
            self.home_url,
            self.login_url,
            self.logout_url,
            self.signup_url,
        )
        for page in urls:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            self.edit_url,
            self.detail_url,
            self.delete_url,
            self.add_url,
            self.list_url,
            self.success_url,
        )
        self.client.force_login(self.author)
        for page in urls:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_create_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for page in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user.username, page=page):
                    url = reverse(page, args=[self.note.slug])
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonym_client(self):
        login_url = reverse('users:login')
        urls = (
            self.add_url,
            self.list_url,
            self.success_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for page in urls:
            with self.subTest(page=page):
                redirect_url = f'{login_url}?next={page}'
                response = self.client.get(page)
                self.assertRedirects(response, redirect_url)
