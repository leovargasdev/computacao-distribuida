import zubaluba
import functools
import requests
import sys
import json
import threading
from bottle import Bottle, route, request, jinja2_view, run, response, redirect, static_file

app = Bottle()
view = functools.partial(jinja2_view, template_lookup=['templates'])
porta = int(sys.argv[1])
servidor = 'http://localhost:3000'

@app.route('/imports/css/<filename>')
def server_static(filename):
    return static_file(filename, root='./imports/css')

@app.route('/estouvivo')
def estou_vivo():
    return json.dumps('Yes baby')

@app.route('/')
@view('index.html')
def index():
    return {'title': 'Página Inicial'}

@app.route('/iniciar', method='POST')
def inicializando_jogador():
    nick = request.forms.get('nick')
    print('nick:', nick)
    jogador = requests.get('{}/jogador/{}'.format(servidor, nick))

    print("jogador", jogador.text)

    redirect('/')


def verificando_servidor():
    try:
        aux = requests.get('{}/add/{}'.format(servidor, porta))
        run(app, host='localhost', port=porta, debug=True, reloader=True)
    except:
        print('Servidor não ativo!')
        return
    time.sleep(10)
    while True:
        try:
            aux_2 = requests.get('{}/estouvivo'.format(servidor))
            print("Servidor", aux_2.text)
        except:
            print("Sem contato com o servidor!!!")
        time.sleep(5)

t1 = threading.Thread(target=verificando_servidor)
t1.start()
