from threading import Event

from flask import Flask, render_template, request, Response, abort
from flask_cors import CORS
from os import listdir
from os.path import splitext, realpath

from src.db import MySQL

import config
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

app.config['pymysql_kwargs'] = {
    'host': config.db_host,
    'port': config.db_port,
    'passwd': config.db_pwd,
    'user': config.db_user,
    'database': config.db_db,
}

themes_file = list(map(lambda file: splitext(file)[0], listdir('templates/themes')))
mysql = MySQL(app)
lock = Event()
lock.set()


@app.route('/', methods=['get'])
def index():
    return render_template('index.html', themes=themes_file)


@app.route('/<user>', methods=['get'])
def visitor(user):
    # user名不合规
    if not match('^[a-zA-Z\d-]*$', user) and user != '_':
        return abort(403)
    referer = sub('^(.*?)/?$', '\\1', request.headers.get('referer', default=''))
    if not (user == '_' or
            referer in [config.domain, 'http://127.0.0.1:5000'] or
            match(f'^https://github\.com/{user}.*?$', referer)
    ):
        return abort(403)
    params = request.args
    active = params.get('active') or ''
    active = active if match('^[0-9a-zA-Z]{6}$', active) else '000000'
    deactive = params.get('deactive') or ''
    deactive = deactive if match('^[0-9a-zA-Z]{6}$', deactive) else 'f1f1f1'
    num = 0
    if user == '_':
        num = 9527
    else:
        # 用户
        conn = mysql.connection
        cursor = mysql.connection.cursor()
        db_user = user
        cursor.execute("select visitors from visitors where id=%s", (db_user,))
        v = cursor.fetchone()
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
                        cursor.execute("insert into visitors (id,visitors,last_view) values (%s, 0, current_date )", (db_user,))
                        old_visitors = 0
                    except:
                        cursor.execute("select visitors from visitors where id=%s", (db_user,))
                        old_visitors = cursor.fetchone()[0]
            if old_visitors is not None:
                # 插入数据
                num = old_visitors + 1
                cursor.execute("update visitors set visitors=%s,last_view=current_date where id=%s", (num, db_user))
            conn.commit()
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
                           theme=params.get('theme') or 'default',
                           active='#' + active,
                           deactive='#' + deactive,
                           animate_speed=max(30, animate_speed),
                           fake_num=[0, 1, 3, 5, 7, 9],
                           size=size,
                           space=space,
                           ).strip()
    return Response(response=resp, headers={
        'Content-Type': 'image/svg+xml',
        'Cache-Control': "no-cache, no-store, must-revalidate",
        'Expires': "0"
    })
