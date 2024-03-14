from threading import Event

from flask import Flask, render_template, request, Response, abort
from flask_cors import CORS
from os import listdir, environ
from os.path import splitext, realpath

import psycopg2

from src.util import num_to_list, default_num_parser, digital_num_parser, list_join
from re import match, sub
from requests import get

app = Flask(__name__)
CORS(app)
app.template_folder = realpath('templates')
app.static_folder = realpath('static')
app.add_template_filter(list_join)
app.add_template_filter(default_num_parser)
app.add_template_filter(digital_num_parser)

themes_file = list(map(lambda file: splitext(file)[0], listdir('templates/themes')))
# import sqlite3
from flask import g

# DATABASE = './database.db'

def get_lock():
    lock = getattr(g, '_lock', None)
    if lock is None:
        lock = g._lock = Event() 
        lock.set()
    return lock

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # db = g._database = sqlite3.connect(DATABASE)
        db = g._database = psycopg2.connect(
			host = environ.get('POSTGRES_HOST'),
			dbname = environ.get('POSTGRES_DATABASE'),
			user = environ.get('POSTGRES_USER'),
			password = environ.get('POSTGRES_PASSWORD'),
			port = environ.get('POSTGRES_PORT'),
		)

    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().cursor()
    cur.execute(query, args)
    rv = cur.fetchone()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/', methods=['get'])
def index():
    return render_template('index.html', themes=themes_file)


@app.route('/<user>', methods=['get'])
def visitor(user):
    params = request.args
    # theme不存在
    theme = params.get('theme') or 'default'
    if theme not in themes_file:
        return abort(403)
    # user名不合规
    if not match('^[a-zA-Z\d-]*$', user) and user != '_':
        return abort(403)
    referer = sub('^(.*?)/?$', '\\1', request.headers.get('referer', default=''))
    user_agent = sub('^(.*?)/?$', '\\1', request.headers.get('User-Agent', default=''))
    from_github = match(f'^https://github\.com/{user}.*?$', referer) or match(f'^github-camo.*?$', user_agent)
    if not (user == '_' or
            referer in [environ.get('HOME_DOMAIN'), 'http://127.0.0.1:5000'] or
            from_github
    ):
        return abort(403)
    active = params.get('active') or ''
    active = active if match('^[0-9a-zA-Z]{6}$', active) else '000000'
    deactive = params.get('deactive') or ''
    deactive = deactive if match('^[0-9a-zA-Z]{6}$', deactive) else 'f1f1f1'
    num = 0
    if user == '_':
        num = 9527
    else:
        lock = get_lock()
        # 用户
        db_user = user
        v = query_db("select visitors from visitors where id=%s", (db_user,))
        old_visitors = None
        lock_v = lock.wait(10)
        if lock_v:
            lock.clear()
            if v:
                old_visitors = v[0]
            else:
                result = get(f'https://api.github.com/users/{user}')
                if result.status_code == 200:
                    # 新增数据
                    try:
                        db = get_db()
                        cur = db.cursor()
                        cur.execute("insert into visitors (id,visitors,last_view) values (%s, 0, current_date )", (db_user,))
                        db.commit()
                        cur.close()
                        old_visitors = 0
                    except:
                        v = query_db("select visitors from visitors where id=%s", (db_user,))
                        if v:
                            old_visitors = v[0]
            if old_visitors is not None:
                num = old_visitors + 1
                if from_github:
                    # 插入数据
                    db = get_db()
                    cur = db.cursor()
                    cur.execute("update visitors set visitors=%s,last_view=current_date where id=%s", (num, db_user))
                    db.commit()
                    cur.close()
            lock.set()

    try:
        animate_speed = min(1000, abs(int(params.get('speed'))))
    except:
        animate_speed = 30
    try:
        length = abs(int(params.get('len')))
    except:
        length = 8
    try:
        size = abs(int(params.get('size')))
    except:
        size = 36
    try:
        space = abs(int(params.get('space')))
    except:
        space = 10
    try:
        show_tail = bool(abs(int(params.get('tail'))))
    except:
        show_tail = True
    num_list = num_to_list(num, length)
    num_string = ''.join(map(lambda x: str(max(0, x)), num_list))
    resp = render_template('visitor.html',
                           num_str=num_string,
                           num=num_list,
                           show_tail=show_tail,
                           valid_len=len(str(num)),
                           theme=theme,
                           active='#' + active,
                           deactive='#' + deactive,
                           animate_speed=max(30, animate_speed),
                           fake_num=[0, 1, 3, 5, 7, 9],
                           size=size,
                           space=space,
                           visitor_width=55,
                           ).strip()
    return Response(response=resp, headers={
        'Content-Type': 'image/svg+xml',
        'Cache-Control': "no-cache, no-store, must-revalidate",
        'Expires': "0"
    })
