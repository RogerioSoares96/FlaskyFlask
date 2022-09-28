from flaskr import create_app

#Check if test config is passed
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

#check hello world route create in init
def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'