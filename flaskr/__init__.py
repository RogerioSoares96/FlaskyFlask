import os

#Check if installing the package on the the VENV does not recognise the syntax ??????
from flask import Flask, render_template, request

#Creating the flask Instance == Flask app through the use of an application factory instead of just app = Flask(__name__) as done before
def create_app(test_config=None):
    #Still creating the app flask in the way below, but since the obj of the app is to scale, more configurations need to be made on this factory app, to allow that scalling
    app = Flask(__name__, instance_relative_config=True)
    #This sets up configurations as default for the app to use
    app.config.from_mapping(
        SECRET_KEY='dev',
        #Creates a path to the database
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    #Test config is checked here to see if it exists, if not a file config.py is loaded instead.
    #This allows for future written tests to be independent of any dev values already configured such as SECRETKEY ETC
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config) 
    #Make sure the instance folder exists because sqlite db file will be created here
    #App instance path refers to the flaskr module as a directory
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    #import the db file from the relative path
    from . import db
    #initiate the close of the db and the cli command through the factory function here
    db.init_app(app)

    #import the auth.py module to add the blue print to the app
    from . import auth
    #adding the blueprint to the app
    app.register_blueprint(auth.bp)
    
    #import the blog.py module to add the blog blue print to the app
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
