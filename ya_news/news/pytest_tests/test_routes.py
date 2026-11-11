from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'url_name',
    [
        'news:home',
        'news:detail',
        'users:login',
        'users:signup',
    ],
)
def test_pages_available_to_anonymous_user(
    client, url_name, news
):
    url = reverse(
        url_name,
        kwargs={'pk': news.pk} if url_name == 'news:detail' else None,
    )

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_name',
    [
        'news:edit',
        'news:delete',
    ],
)
def test_author_can_access_comment_pages(
    author_client, url_name, comment
):
    url = reverse(url_name, args=(comment.pk,))

    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_name',
    [
        'news:edit',
        'news:delete',
    ],
)
def test_other_user_cannot_access_comment_pages(
    reader_client, url_name, comment
):
    url = reverse(url_name, args=(comment.pk,))

    response = reader_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_name',
    [
        'news:edit',
        'news:delete',
    ],
)
def test_anonymous_user_redirected_to_login(
    client, url_name, comment, login_url
):
    url = reverse(url_name, args=(comment.pk,))

    response = client.get(url)

    parsed_url = urlparse(response.url)

    assert response.status_code == HTTPStatus.FOUND
    assert parsed_url.path == login_url
    assert parse_qs(parsed_url.query) == {'next': [url]}


def test_logout_by_post(author_client, logout_url):
    author_client.post(logout_url)

    assert '_auth_user_id' not in author_client.session
