from http import HTTPStatus

import pytest

from news.models import Comment


COMMENT_DATA = {'text': 'Новый комментарий'}

BAD_WORDS_DATA = (
    {'text': 'редиска'},
    {'text': 'негодяй'},
)

WARNING = 'Не ругайтесь!'


def test_anonymous_user_cannot_create_comment(client, detail_url, news):
    response = client.post(detail_url, data=COMMENT_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.exists()


def test_authorized_user_can_create_comment(
    author_client, detail_url, detail_url_with_comments, author, news
):
    response = author_client.post(detail_url, data=COMMENT_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_with_comments
    assert Comment.objects.count() == 1

    comment = Comment.objects.get(news=news)

    assert comment.text == COMMENT_DATA['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.parametrize('data', BAD_WORDS_DATA)
def test_comment_with_bad_word_is_not_created(
    author_client, detail_url, data
):
    response = author_client.post(detail_url, data=data)

    assert response.status_code == HTTPStatus.OK
    assert WARNING in response.context['form'].errors['text']
    assert not Comment.objects.exists()


def test_author_can_edit_comment(
    author_client, edit_url, detail_url_with_comments, comment
):
    response = author_client.post(edit_url, data=COMMENT_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_with_comments

    updated_comment = Comment.objects.get(pk=comment.pk)

    assert updated_comment.text == COMMENT_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_author_can_delete_comment(
    author_client, delete_url, detail_url_with_comments, comment
):
    response = author_client.post(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_with_comments
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_reader_cannot_edit_comment(
    reader_client, edit_url, comment
):
    response = reader_client.post(edit_url, data=COMMENT_DATA)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()

    unchanged_comment = Comment.objects.get(pk=comment.pk)

    assert unchanged_comment.text == comment.text
    assert unchanged_comment.author == comment.author
    assert unchanged_comment.news == comment.news


def test_reader_cannot_delete_comment(
    reader_client, delete_url, comment
):
    response = reader_client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()

    unchanged_comment = Comment.objects.get(pk=comment.pk)

    assert unchanged_comment.text == comment.text
    assert unchanged_comment.author == comment.author
    assert unchanged_comment.news == comment.news
