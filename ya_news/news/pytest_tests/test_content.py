import pytest

from news.forms import CommentForm
from django.conf import settings


pytestmark = pytest.mark.django_db


def test_news_page(client, home_url):
    """Проверка вывода кол-во новостей на странице"""
    response = client.get(home_url)
    object_list = response.context.get('object_list')
    assert object_list is not None
    assert object_list.count() <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_news(client, home_url):
    """Проверка сортировки новостей"""
    response = client.get(home_url)
    object_list = response.context.get('object_list')
    assert object_list is not None
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments(client, detail_url, news):
    """Проверка сортировки комментариев по времени"""
    response = client.get(detail_url)
    comments = response.context.get('news')
    assert comments is not None
    comments_set = news.comment_set.all()
    all_comments = [comment.created for comment in comments_set]
    sorted_comments = sorted(all_comments)
    assert all_comments == sorted_comments


@pytest.mark.parametrize(
    'key, value',
    (
        (pytest.lazy_fixture('user_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_form_show_correct_user(key, value, detail_url):
    """Проверка формы для отправки комментариев"""
    response = key.get(detail_url)
    assert isinstance(response.context.get('form'), CommentForm) is value
