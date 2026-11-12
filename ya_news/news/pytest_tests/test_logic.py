from http import HTTPStatus

from news.models import Comment


COMMENT_DATA = {'text': 'Новый комментарий'}
EDITED_COMMENT_DATA = {'text': 'Изменённый комментарий'}
BAD_WORD = 'Ты редиска!'
BAD_WORD_DATA = {'text': BAD_WORD}
BAD_WORD_ERROR = 'Не ругайтесь!'
OTHER_COMMENT_DATA = {'text': 'Чужое изменение'}


def test_anonymous_user_cannot_create_comment(client, detail_url, news):
    response = client.post(detail_url, data=COMMENT_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.exists()


def test_authorized_user_can_create_comment(
    author_client, detail_url, detail_url_with_comments, author, news
):
    response = author_client.post(detail_url, data=COMMENT_DATA)

    comment = Comment.objects.order_by('pk').last()

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_with_comments
    assert Comment.objects.count() == 1
    assert comment.text == COMMENT_DATA['text']
    assert comment.author == author
    assert comment.news == news


def test_comment_with_bad_word_is_not_created(
    author_client, detail_url, news
):
    response = author_client.post(detail_url, data=BAD_WORD_DATA)

    assert response.status_code == HTTPStatus.OK
    assert BAD_WORD_ERROR in response.context['form'].errors['text']
    assert not Comment.objects.exists()


def test_author_can_edit_comment(
    author_client, edit_url, detail_url_with_comments, comment
):
    original_author_id = comment.author_id
    original_news_id = comment.news_id

    response = author_client.post(
        edit_url,
        data=EDITED_COMMENT_DATA,
    )

    comment.refresh_from_db()

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_with_comments
    assert comment.text == EDITED_COMMENT_DATA['text']
    assert comment.author_id == original_author_id
    assert comment.news_id == original_news_id


def test_author_can_delete_comment(
    author_client, delete_url, detail_url_with_comments, comment
):
    response = author_client.post(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_with_comments
    assert not Comment.objects.exists()


def test_other_user_cannot_edit_comment(reader_client, edit_url, comment):
    original_text = comment.text
    original_author_id = comment.author_id
    original_news_id = comment.news_id

    response = reader_client.post(
        edit_url,
        data=OTHER_COMMENT_DATA,
    )

    comment.refresh_from_db()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == original_text
    assert comment.author_id == original_author_id
    assert comment.news_id == original_news_id


def test_other_user_cannot_delete_comment(
    reader_client, delete_url, comment
):
    original_text = comment.text
    original_author_id = comment.author_id
    original_news_id = comment.news_id

    response = reader_client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()

    comment.refresh_from_db()

    assert comment.text == original_text
    assert comment.author_id == original_author_id
    assert comment.news_id == original_news_id
