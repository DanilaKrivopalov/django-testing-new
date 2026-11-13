from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


User = get_user_model()


@pytest.fixture
def author(db):
    return User.objects.create_user(
        username='author',
        password='password123',
    )


@pytest.fixture
def reader(db):
    return User.objects.create_user(
        username='reader',
        password='password123',
    )


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости.',
    )


@pytest.fixture
def comment(db, author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Тестовый комментарий.',
    )


@pytest.fixture
def news_list(db):
    News.objects.bulk_create(
        News(
            title=f'Новость {number}',
            text=f'Текст новости {number}.',
            date=timezone.localdate() + timedelta(days=number),
        )
        for number in range(11)
    )


@pytest.fixture
def comments(db, author, news):
    comments = Comment.objects.bulk_create(
        Comment(
            news=news,
            author=author,
            text=f'Комментарий {number}',
        )
        for number in range(333)
    )

    current_time = timezone.now()

    for number, comment in enumerate(comments):
        comment.created = current_time - timedelta(minutes=number)

    Comment.objects.bulk_update(comments, ['created'])


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def detail_url_with_comments(detail_url):
    return f'{detail_url}#comments'


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def edit_redirect_url(login_url, edit_url):
    return f'{login_url}?next={edit_url}'


@pytest.fixture
def delete_redirect_url(login_url, delete_url):
    return f'{login_url}?next={delete_url}'


@pytest.fixture
def logout_url():
    return reverse('users:logout')
