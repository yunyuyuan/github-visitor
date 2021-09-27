from flask import Flask, render_template, request, Response
from flask_cors import CORS
from os import listdir
from os.path import splitext, realpath
from src.util import num_to_list, svg_encode, default_num_parser, digital_num_parser
from re import match

app = Flask(__name__)
CORS(app)
app.template_folder = realpath('templates')
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
        length = abs(int(params.get('len')))
    except:
        length = 8
    resp = render_template('visitor.html',
                           num=num_to_list(num, length),
                           theme=params.get('theme') or 'default',
                           active='#'+active,
                           deactive='#'+deactive,
                           ).strip()
    return Response(response=render_template('img.html', img='data:image/svg+xml,'+svg_encode(resp)))
