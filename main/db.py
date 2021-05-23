import sqlite3
import click
import shutil
from flask import current_app,g
from flask.cli import with_appcontext
import os

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
 

    db = g.pop('db', None)
    if db is not None:
        db.close()



def init_db():

    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    if os.path.isdir("./main/static/image"):
        shutil.rmtree("./main/static/image")


@click.command('init-db')
@with_appcontext
def init_db_command():

    click.echo("----------------------------------------------------------------------------")
    click.echo("init_db_command() : add_command로 설정한 init_db_command가 실행됐습니다")
   
    init_db()
    click.echo('init_db_command() : schema.sql를 기본값으로 데이터베이스를 초기화 했습니다.')

def init_app(app):

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

