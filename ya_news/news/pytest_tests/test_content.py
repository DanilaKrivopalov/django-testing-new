from news.forms import CommentForm


def test_news_count_on_home_page(client, home_url, news_list):
    assert len(client.get(home_url).context['object_list']) == 10


def test_news_order_on_home_page(client, home_url, news_list):
    actual_dates = [
        news.date
        for news in client.get(home_url).context['object_list']
    ]

    assert actual_dates == sorted(actual_dates, reverse=True)


def test_comments_order_on_news_page(client, detail_url, comments):
    actual_dates = [
        comment.created
        for comment in client.get(detail_url).context[
            'news'
        ].comment_set.all()
    ]

    assert actual_dates == sorted(actual_dates)


def test_anonymous_user_does_not_see_comment_form(client, detail_url):
    assert 'form' not in client.get(detail_url).context


def test_authorized_user_sees_comment_form(author_client, detail_url):
    context = author_client.get(detail_url).context

    assert 'form' in context
    assert isinstance(context['form'], CommentForm)
