import sqlite3

import click
from flask import current_app, g


def get_db():
    #g serves the purpose of keeping data alive through a request, in the case of the access to a db multiple times in a request g maintains the connection to DB in this case stored
    if 'db' not in g:
        #connect to the file Pointed by Databse in the __init__.py path even if not created it.
        g.db = sqlite3.connect(
            #Current app points to the app handling the request since I used a factory function before, there is no App object (app = Flask(...)) so this handles the pointing to the app that is performing the request. Get is only used when the app is created so the use of this makes sense
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        #sqlite3.row will return a list of rows as a list of dicts, List of dicts as rows when the file is created.
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None):
    #checks if the DB is was set
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    #initialise the db by getting the database connection through get_db, this will return the path
    db = get_db()
    #this will read all the instructions on the schema in order to create the db file with the correct use of the rows as mentioned above and with the rules from schema
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


#crate cli command to initiate the DB.
@click.command('init-db')
def init_db_command():
    #clear existing data and create new tables
    init_db()
    #success message
    click.echo('Initialized the database')

#This function allows for the start and closing of the DB to be done through the factory function.
def init_app(app):
    #this allows for the close of the DB whenever the request is finished
    app.teardown_appcontext(close_db)
    #this allows for the use of the click command through the terminal with the "flask" command before
    app.cli.add_command(init_db_command)
