from crypt import methods
import functools
from operator import methodcaller
from urllib import response


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
#Used before creating password hashes and what not
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

#Blue print serves the purpose of organising a group of related views, I.e : www.sfhjdsk.com/auth -> /auth will be the blue print, this will store a common pattern for /auth parts of the webapp, view functions are associated with blueprints when dispatching requests and responses
#Blueprint name is auth, calls itself as a package and has the below prefix
bp = Blueprint('auth', __name__, url_prefix='/auth')

#From the auth route we create a new view "Register", so this view stays under the auth blueprint
@bp.route('/register', methods=('GET', 'POST'))
def register():
    #Getting a form back through Post
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #getting back the DB
        db = get_db()
        #Setting an error
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                #Commit method to commit the changes made above to the DB
                db.commit()
            #integrity error happens if in this case a username already exists
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
            #Fetches only one row returns either one record or None
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            #session behaves like a dict to save data across requests
            #the data is then stored in a cookie and sent to browser securely signed
            #at the beggining of other requests this session id should be loaded if the user is logged in
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
    
    return render_template('auth/login.html')

#This function runs before any other view function URL from /auth
@bp.before_app_request
def load_logged_in_user(): #This function loads the user to be done before any any other view function from /auth
    user_id = session.get('user_id') #load user from sesh
    # load user data to g.user keeping that data "alive during the request"
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone

@bp.route('/logout')
def logout():
    #Clearing the session deletes de user id from Session allowing the app to be resetted into a clean session state
    session.clear()
    return redirect(url_for('index'))

#essentially this function is to be used as a decorator in order to check in certains routes that the user needs to be logged in
def login_required(view):
    #this wraps the view with the wrapped view function in order to obtain the information stated above
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            #if not user is loaded meaning no login, the user is sent back to login page
            return redirect(url_for('auth.login'))
        #suspect the Kwarg being returned is the user ID TBC
        return view(**kwargs)
    return wrapped_view