from http import HTTPStatus

import pytest
from django.urls import reverse

from news.models import Comment


def test_anonymous_user_cannot_create_comment(
    client, detail_url, news
):
    comments_count = Comment.objects.count()

    response = client.post(
        detail_url,
        data={'text': 'Новый комментарий'},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_count


def test_authorized_user_can_create_comment(
    author_client, detail_url, author, news
):
    comments_count = Comment.objects.count()
    text = 'Новый комментарий'

    response = author_client.post(
        detail_url,
        data={'text': text},
    )

    comment = Comment.objects.get(
        news=news,
        author=author,
        text=text,
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{detail_url}#comments'
    assert Comment.objects.count() == comments_count + 1
    assert comment.text == text
    assert comment.author == author
    assert comment.news == news


def test_comment_with_bad_word_is_not_created(
    author_client, detail_url, news
):
    comments_count = Comment.objects.count()

    response = author_client.post(
        detail_url,
        data={'text': 'Ты редиска!'},
    )

    assert response.status_code == HTTPStatus.OK
    assert 'Не ругайтесь!' in response.context['form'].errors['text']
    assert Comment.objects.count() == comments_count


def test_author_can_edit_comment(
    author_client, edit_url, comment, author, news
):
    new_text = 'Изменённый комментарий'

    response = author_client.post(
        edit_url,
        data={'text': new_text},
    )

    updated_comment = Comment.objects.get(pk=comment.pk)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == (
        reverse('news:detail', args=(news.pk,)) + '#comments'
    )
    assert updated_comment.text == new_text
    assert updated_comment.author == author
    assert updated_comment.news == news


def test_author_can_delete_comment(
    author_client, delete_url, comment, news
):
    response = author_client.post(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == (
        reverse('news:detail', args=(news.pk,)) + '#comments'
    )
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.parametrize(
    'url_name',
    [
        'news:edit',
        'news:delete',
    ],
)
def test_other_user_cannot_change_comment(
    reader_client, comment, url_name
):
    original_text = comment.text
    original_author = comment.author
    original_news = comment.news

    url = reverse(url_name, args=(comment.pk,))

    response = reader_client.post(
        url,
        data={'text': 'Чужое изменение'},
    )

    unchanged_comment = Comment.objects.get(pk=comment.pk)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert unchanged_comment.text == original_text
    assert unchanged_comment.author == original_author
    assert unchanged_comment.news == original_news
