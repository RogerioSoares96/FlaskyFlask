import sqlite3

import pytest
from flaskr.db import get_db

#This test checks that the connection to the DB returns the same db each time and is closes the same each time
def test_get_close_db(app):
    #Adding app context  to the obj arg passed above
    with app.app_context():
        db = get_db()
        assert db is get_db()
    #Verify if the sqlite3 programming error is triggered when the db executes the command below.
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    #Check if word closed in the error raised above
    assert 'closed' in str(e.value)

#This test runs in order to check that the init sends a message and verifies if the command was already called throught the use of the monkey patch below.
def test_init_db_command(runner, monkeypatch):
    #Creates a class that records the status of the call to init db
    class Recorder(object):
        called = False
    #returns a true call for fake init db
    def fake_init_db():
        Recorder.called = True
    #Set the fake_init_db attribute = true to the flask.db command, because if the command is called the recorder is set to true, if the command is not called the recorder is set to false
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    #runner will call the init-db command on the CLI
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    #at the end recorder is called to see if the command was called above 
    assert Recorder.called
