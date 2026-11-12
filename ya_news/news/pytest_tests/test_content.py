from django.conf import settings

from news.forms import CommentForm


def test_news_count_on_home_page(client, home_url, news_list):
    response = client.get(home_url)

    assert len(response.context['object_list']) == (
        settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_order_on_home_page(client, home_url, news_list):
    actual_dates = [
        news.date
        for news in client.get(home_url).context['object_list']
    ]

    expected_dates = sorted(
        [news.date for news in news_list],
        reverse=True,
    )[:settings.NEWS_COUNT_ON_HOME_PAGE]

    assert actual_dates == expected_dates


def test_comments_order_on_news_page(client, detail_url, comments):
    response = client.get(detail_url)

    actual_comments = [
        comment.text
        for comment in response.context['news'].comment_set.all()
    ]

    expected_comments = [
        'Комментарий 0',
        'Комментарий 1',
        'Комментарий 2',
    ]

    assert actual_comments == expected_comments


def test_anonymous_user_does_not_see_comment_form(client, detail_url):
    assert 'form' not in client.get(detail_url).context


def test_authorized_user_sees_comment_form(author_client, detail_url):
    context = author_client.get(detail_url).context

    assert 'form' in context
    assert isinstance(context['form'], CommentForm)
