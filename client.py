import zubaluba
import functools
import requests
import sys
import json
import threading
import time
from bottle import Bottle, route, request, jinja2_view, run, response, redirect, static_file

app = Bottle()
view = functools.partial(jinja2_view, template_lookup=['templates'])

porta = int(sys.argv[1])
servidor = 'http://localhost:3000'
pergunta = jogador = ''

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
    global jogador

    nick = request.forms.get('nick')
    jogador = json.loads(requests.get('{}/jogador/{}'.format(servidor, nick)).text)
    redirect('/usr/{}/pergunta'.format(nick))

@app.route('/usr/<nick>/pergunta', method='GET')
@view('pergunta.html')
def carregar_pergunta(nick):
    global pergunta
    global jogador

    pergunta = json.loads(requests.get('{}/pergunta'.format(servidor)).text)
    return {'jogador': jogador, 'piadinha': pergunta, 'title': 'Pergunta'}

@app.route('/responder', method='POST')
def verifica_resposta():
    global pergunta
    global jogador

    aux = {'resposta': request.forms.get('resposta'), 'id': pergunta['_id']}
    aux = json.dumps(aux)
    jogador = requests.get('{}/usr/{}/responder/{}'.format(servidor, jogador['nick'], aux))
    jogador = json.loads(jogador.text)
    if jogador['winner']:
        jogador['winner'] = json.loads(jogador['winner'])
        if jogador['winner']['nick'] == jogador['nick']:
            redirect('/winner')
        redirect('/loser')
    redirect('/usr/{}/pergunta'.format(jogador['nick']))

@app.route('/winner', method='GET')
@view('winner.html')
def mostra_winner():
    global jogador
    return {'jogador': jogador['winner'], 'title': 'Um winner'}

@app.route('/loser', method='GET')
@view('loser.html')
def mostra_loser():
    global jogador
    print("loser:", jogador)
    return {'jogador': jogador, 'title': 'Um loser'}

def status_servidor():
    try:
        aux = requests.get('{}/add/{}'.format(servidor, porta))
        return True
    except:
        print('Servidor não ativo!')
    return False

def verificando_servidor():
    time.sleep(10)
    while True:
        try:
            aux = requests.get('{}/estouvivo'.format(servidor))
            print("Servidor diz:", str(aux.text))
        except:
            print("Sem contato com o servidor!!!")
        time.sleep(12)

def situacao_jogo():
    time.sleep(5)
    while True:
        try:
            aux = requests.get('{}/situacaoJogo'.format(servidor))
            aux = str(aux.text).replace('\"', '').split('__')
            for k in aux:
                k = k.split('#')
                print("Jogador:", k[0] + "\tPontos:", k[1])
        except:
            print("Sem contato com o servidor!!!")
        time.sleep(20)

if status_servidor():
    t1 = threading.Thread(target=verificando_servidor)
    t1.start()

    t2 = threading.Thread(target=situacao_jogo)
    t2.start()

    run(app, host='localhost', port=porta)
