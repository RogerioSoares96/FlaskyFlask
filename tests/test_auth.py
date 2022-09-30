import pytest
from flask import g, session
from flaskr.db import get_db


#Verifyfies page is up rendering(200), create mock user A pword A, verify response header location = login after registering user, verifies if user is in DB, Data can also be compared as part of the test check - https://flask.palletsprojects.com/en/2.2.x/tutorial/tests/#:~:text=data%20contains%20the%20body%20of%20the%20response%20as%20bytes.%20If%20you%20expect%20a%20certain%20value%20to%20render%20on%20the%20page%2C%20check%20that%20it%E2%80%99s%20in%20data.%20Bytes%20must%20be%20compared%20to%20bytes.%20If%20you%20want%20to%20compare%20text%2C%20use%20get_data(as_text%3DTrue)%20instead.
def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

#Asking pytest to parametrize the test with multiple different inputs , so no need to write code 3 times. Expected error messages are also described
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
#test to run with the parameters set above
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        #this is the data to be posted 
        data={'username': username, 'password': password}
    )
    assert message in response.data

#Same as register
def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"
    #Verify session data through "with" as the session data is only available after thge response is returned
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user()['username'] == 'test'

#Again paremetrizing data onto the input
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

#logout
def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session