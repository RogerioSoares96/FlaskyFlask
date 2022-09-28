from flaskr import create_app

#Not a lot to test in the factory other than checking if the test config is passed in order to see if any default config needs to be implemented  then sanity checking the hello route
#Check if test config is passed
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

#check hello world route create in init
def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'