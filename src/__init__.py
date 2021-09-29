from flask import Flask, render_template, request, Response
from flask_cors import CORS
from os import listdir
from os.path import splitext, realpath
from src.util import num_to_list, svg_encode, default_num_parser, digital_num_parser, list_join
from re import match

app = Flask(__name__)
CORS(app)
app.template_folder = realpath('templates')
app.add_template_filter(list_join)
app.add_template_filter(default_num_parser)
app.add_template_filter(digital_num_parser)

themes_file = list(map(lambda file: splitext(file)[0], listdir('templates/themes')))


@app.route('/', methods=['get'])
def index():
    return render_template('index.html', themes=themes_file)


@app.route('/<user>', methods=['get'])
def visitor(user):
    params = request.args
    active = params.get('active') or ''
    active = active if match('^[0-9a-zA-Z]{6}$', active) else '000000'
    deactive = params.get('deactive') or ''
    deactive = deactive if match('^[0-9a-zA-Z]{6}$', deactive) else 'f1f1f1'
    num = 0
    if user == '_':
        num = 9527
    else:
        pass
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
    resp = render_template('visitor.html',
                           num=num_to_list(num, length),
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
        'Content-Type': 'image/svg+xml'
    })
