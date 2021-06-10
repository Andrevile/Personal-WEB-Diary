from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import click
from werkzeug.utils import secure_filename
from main.log import login_required
from main.db import get_db
import base64
import os
import shutil
count=0
def get_post(id, check_author=True):
    
  

    post = get_db().execute(
        'SELECT p.id, title, body, created, picture,author_id,username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()
    
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    

    return post

bp = Blueprint('diary', __name__)
@bp.route('/')
def index():
  
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, picture,author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    
    # get_image=posts[0]['picture']
    # print(get_image)

    return render_template('diary/index.html', posts=posts )

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    global count

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        picture=request.files['reviewImg']
        error = None
        
        
        picture_name=picture.filename
        
        if not title:
            error = '제목이 필요합니다.'

        if error is not None:
            flash(error)
        
        
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, picture,author_id)'
                ' VALUES (?, ?,?,?)',
                (title, body,picture_name,g.user['id'])
            )
            db.commit()
            count+=1
            print(count)
            if count!=0:
               # post=get_post(count)
               # print("post title:{}".format(post['title']))
               # print("create post[id]:{}".format(post['id']))
                # post=get_post(g.user['id'])
                # print(post, post['id'])
                #print(count)
                if picture:
                    os.makedirs("./main/static/image/"+str(g.user['id'])+"/"+str(count),mode=777)
                    picture.save("./main/static/image/"+str(g.user['id'])+"/"+str(count)+"/"+"1.jpg")
                    
            return redirect(url_for('diary.index'))

    return render_template('diary/create.html')



@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    global count

    post = get_post(id)
    print("update count:{}".format(count))
    print("post id:{}".format(post['id']))
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        picture=request.files['reviewImg']
        
        picture_name=picture.filename
        error = None

        if not title:
            error = '제목이 필요합니다.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?,picture= ?'
                ' WHERE id = ?',
                (title, body,picture_name ,id)
            )
            db.commit()
            
            if picture:
                if post['picture']:
                    picture.save("./main/static/image/"+str(g.user['id'])+"/"+str(post['id'])+"/"+"1.jpg")
                else:
                    os.makedirs("./main/static/image/"+str(g.user['id'])+"/"+str(post['id']),mode=777)
                    picture.save("./main/static/image/"+str(g.user['id'])+"/"+str(post['id'])+"/"+"1.jpg")
            else:
                if post['picture']:
                    shutil.rmtree("./main/static/image/"+str(g.user['id'])+"/"+str(post['id']))

            
            return redirect(url_for('diary.index'))
    return render_template('diary/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    global count
    post=get_post(id)
    if post['picture']:   
         shutil.rmtree("./main/static/image/"+str(g.user['id'])+"/"+str(post['id'])) ##하위만 삭제하므로 나중에 해당폴더 삭제 조사
  
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    
    print(count)
    
    return redirect(url_for('diary.index'))
