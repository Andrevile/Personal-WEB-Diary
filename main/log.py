import functools
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from main.db import get_db


bp = Blueprint('log', __name__, url_prefix='/log')

@bp.route('/check')
def check():
    return "test"
@bp.route('/register', methods=('GET', 'POST'))
def register():
  
    if request.method == 'POST':
       
        username = request.form['username']
        password = request.form['password']
        db = get_db() 
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = '{}는 이미 존재하는 사용자입니다.'.format(username)

        if error is None:
            db.execute(
               
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()

            
            return redirect(url_for('log.login'))
        
        flash(error)


    return render_template('log/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'ID가 존재하지 않습니다.'
        elif not check_password_hash(user['password'], password):
            error = '틀린 비밀번호 입니다.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('log/login.html')

@bp.before_app_request
def load_logged_in_user():

    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()    
    

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('log.login'))

        return view(**kwargs)

    return wrapped_view