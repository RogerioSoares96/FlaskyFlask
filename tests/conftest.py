import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

#Opening the data.sql file as as reading in binary through joining the dirname of this file and the path of the sql file. Reading into the data_sql variable
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

#fixtures are the pre conditions to the testing of the app
#pytest fixture app will allow us to call the factory function and create the app not with the dev settings but with the test settings.
@pytest.fixture
def app():
    #tempfile creates a temporary file with a kernel open file descriptor and its path
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        #Let's Flask Know the app is in testing mode
        'TESTING': True,
        #db is pointing to the path of the temporary file path whilst the test is Running
        'DATABASE': db_path,
    })

    #App context refers to the app created above, so the db commands listed below are executed with the context of the app just created
    with app.app_context():
        init_db()
        #executes the sql script onto the temp file created
        get_db().executescript(_data_sql)
    #Return a generator object from the app that will only run once ?? Continuing from where it left off
    yield app

    os.close(db_fd)
    #Deleting file Path
    os.unlink(db_path)

#This fixture client is used to call the test_client in order to create a test client for the specific app, this allows for a "client" to be created and to run tests w/o running a server
@pytest.fixture
def client(app):
    return app.test_client()

#This fixture runner is used to create a test runner for the specific app that allows it to call all click commands registered with the app used, to then invoke the functions. sort of server-side testing basis vs the client side above mentioned
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

#Create a class to simulate a logged in user so this does not to be written everytime a test is made on a view, the client passes this with a fixture for each test 
class AuthActions(object):
    #Add the methods to login lgout, identify client
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

#Add it as as fixture as the user and pword have been already inserted with the app fixture.
@pytest.fixture
def auth(client):
    return AuthActions(client)