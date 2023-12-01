from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        """Тест проверяет 1 и 2 задание.
        1-Отдельная заметка передаётся на страницу со списком заметок в списке
        object_list в словаре context;
        2-в список заметок одного пользователя не попадают
        заметки другого пользователя;
        """
        users_notes = (
            (self.author, True),
            (self.reader, False),
        )
        for user, note_in_list in users_notes:
            self.client.force_login(user)
            with self.subTest(user=user.username, note_in_list=note_in_list):
                response = self.client.get(reverse('notes:list'))
                object_list = response.context.get('object_list')
                self.assertIsNotNone(object_list)
                note_in_object_list = self.note in object_list
                self.assertEqual(note_in_object_list, note_in_list)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for page, args in urls:
            with self.subTest(page=page):
                self.client.force_login(self.author)
                response = self.client.get(reverse(page, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
