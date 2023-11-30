from django.urls import reverse

from http import HTTPStatus

from pytest_django.asserts import assertRedirects
import pytest


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news_id'))
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, args):
    response = client.get(reverse(name, args=args))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (('news:edit', pytest.lazy_fixture('comment_id')),
     ('news:delete', pytest.lazy_fixture('comment_id')),),
)
def test_availability_for_comment_edit_and_delete(author_client, name, args):
    response = author_client.get(reverse(name, args=args))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'page, args',
    (('news:edit', pytest.lazy_fixture('comment_id')),
     ('news:delete', pytest.lazy_fixture('comment_id')),),
)
def test_redirects(client, page, args):
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={reverse(page, args=args)}'
    response = client.get(reverse(page, args=args))
    assertRedirects(response, expected_url)


@pytest.mark.parametrize('page', ('news:edit', 'news:delete'))
def test_pages_availability_for_different_users(
        page, comment_id, admin_client
):
    response = admin_client.get(reverse(page, args=comment_id))
    assert response.status_code == HTTPStatus.NOT_FOUND
