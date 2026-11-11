from http import HTTPStatus

from news.forms import CommentForm


def test_news_count_on_home_page(client, home_url, news_list):
    response = client.get(home_url)

    assert response.status_code == HTTPStatus.OK
    assert len(response.context['object_list']) == 10


def test_news_order_on_home_page(client, home_url, news_list):
    response = client.get(home_url)

    actual_dates = [
        news.date for news in response.context['object_list']
    ]
    expected_dates = sorted(
        [news.date for news in news_list],
        reverse=True,
    )[:10]

    assert actual_dates == expected_dates


def test_comments_order_on_news_page(
    client, detail_url, comments
):
    response = client.get(detail_url)

    actual_comments = list(
        response.context['news'].comment_set.all()
    )

    assert actual_comments == comments


def test_anonymous_user_does_not_see_comment_form(
    client, detail_url
):
    response = client.get(detail_url)

    assert 'form' not in response.context


def test_authorized_user_sees_comment_form(
    author_client, detail_url
):
    response = author_client.get(detail_url)

    assert isinstance(response.context['form'], CommentForm)
