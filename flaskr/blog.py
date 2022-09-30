from crypt import methods
from turtle import title
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

#Adding the previous work
from flaskr.auth import login_required
from flaskr.db import get_db

#creating a value print w/o url prefix since some views on auth,py referred to 
bp = Blueprint('blog', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post AS p JOIN user AS u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None
        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user()['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template("blog/create.html")

#This function serves to check if the author of the post matches the id of the post, will serve the update and delete function
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post AS p JOIN user AS u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} does not exist")
    if check_author and post['author_id'] != g.user()['id']:
        abort(403)
    return post

@bp.route('/<int:id>/update', methods = ('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods = ('GET', 'POST'))
@login_required
def delete(id):
    post = get_post(id)
    if request.method == 'POST':
        db = get_db()
        db.execute('DELETE FROM post WHERE id = ?',(id,))
        db.commit()
        return redirect(url_for('blog.index'))