from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.models import Comment
from news.forms import WARNING


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(detail_url, client,
                                            form_data_comment, login_url):
    """Проверка доступа к коментарияем не зарег. пользователя"""
    response = client.post(detail_url, data=form_data_comment)
    comments_count = Comment.objects.count()
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert comments_count == 0


def test_user_can_create_comment(
        author,
        detail_url,
        form_data_comment,
        news,
        user_client
):
    """Проверка создания коментария зарег. пользователем"""
    response = user_client.post(detail_url, data=form_data_comment)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data_comment['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_user_cant_use_bad_words(bad_words_data, detail_url, user_client):
    """Проверка запрещенных слов"""
    response = user_client.post(detail_url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(detail_url, user_client,
                                 form_data_comment, news,
                                 author, comment):
    """Проверка редактирования комментария зарег. пользователем"""
    response = user_client.post(detail_url, form_data_comment)
    assertRedirects(response, f'{detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data_comment['text']
    assert comment.news == news
    assert comment.author == author


def test_author_can_delete_comment(detail_url, delete_url, user_client):
    """Проверка, что автор может удалить комментарий"""
    response = user_client.post(delete_url)
    assertRedirects(response, detail_url + '#comments')
    assert Comment.objects.count() == 0


def test_reader_cant_edit_comment_of_another_user(
        admin_client,
        edit_url,
        form_data_comment,
        comment
):
    """Проверка доступа только к своим коментариям"""
    response = admin_client.post(edit_url, form_data_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


def test_user_cant_delete_comment_of_another_user(detail_url, delete_url,
                                                  user_client):
    """Проверка, что пользователи могут удалять только свои комментарии"""
    response = user_client.post(delete_url)
    assertRedirects(response, detail_url + '#comments')
    assert Comment.objects.count() == 0
