import functools
from bottle import Bottle, request, route, jinja2_view, run, response, redirect, static_file, sys

app = Bottle()

view = functools.partial(jinja2_view, template_lookup=['templates'])

peers = sys.argv[2:]
porta = int(sys.argv[1])
contador = 0
@app.route('/imports/css/<filename>')
def server_static(filename):
    return static_file(filename, root='./imports/css')

# [PÁGINA] Home
@app.route('/')
@view('index.html')
def index():
    return {'menu': "perdi", 'title': 'home', 'peers': peers, 'numero': contador}

@app.route('/contador', method='POST')
def teste():
    global contador
    contador = contador + 100
    redirect('/')

@app.route('/contador', method='GET')
def teste():
    global contador
    contador = contador + 1
    redirect('/')

run(app, host='localhost', port=porta, debug=True, reloader=True)
