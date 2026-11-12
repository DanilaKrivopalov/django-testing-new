from http import HTTPStatus


def test_status_codes(
    client,
    author_client,
    reader_client,
    home_url,
    detail_url,
    login_url,
    signup_url,
    edit_url,
    delete_url,
    subtests,
):
    test_cases = [
        (home_url, client, HTTPStatus.OK),
        (detail_url, client, HTTPStatus.OK),
        (login_url, client, HTTPStatus.OK),
        (signup_url, client, HTTPStatus.OK),
        (edit_url, author_client, HTTPStatus.OK),
        (delete_url, author_client, HTTPStatus.OK),
        (edit_url, reader_client, HTTPStatus.NOT_FOUND),
        (delete_url, reader_client, HTTPStatus.NOT_FOUND),
    ]

    for url, user_client, expected_status in test_cases:
        with subtests.test(url=url, expected_status=expected_status):
            assert user_client.get(url).status_code == expected_status


def test_redirects(
    client,
    author_client,
    edit_url,
    delete_url,
    login_url,
    logout_url,
    subtests,
):
    redirect_cases = [
        (edit_url, f'{login_url}?next={edit_url}'),
        (delete_url, f'{login_url}?next={delete_url}'),
    ]

    for url, expected_url in redirect_cases:
        with subtests.test(url=url):
            response = client.get(url)

            assert response.url == expected_url

    author_client.post(logout_url)

    assert '_auth_user_id' not in author_client.session
