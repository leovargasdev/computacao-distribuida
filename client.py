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
    result = []
    jogadores = requests.get('{}/situacaoJogo'.format(servidor))
    jogadores = str(jogadores.text).replace('\"', '').split('__')
    if 1 < len(jogadores):
        for j in jogadores:
            if j != '':
                j = j.split('#')
                result.append({'pts': j[1],'nome': j[0]})
    return {'title': 'Página Inicial', 'jogadores': result}

@app.route('/iniciar', method='POST')
def inicializando_jogador():
    nick = request.forms.get('nick')
    nick = nick.replace(' ', '_')
    redirect('/usr/{}'.format(nick))

@app.route('/usr/<nick>', method='GET')
def carregando_jogador(nick):
    global jogador
    jogador = json.loads(requests.get('{}/jogador/{}'.format(servidor, nick)).text)
    redirect('/pergunta')

@app.route('/pergunta', method='GET')
@view('pergunta.html')
def carregar_pergunta():
    global pergunta
    global jogador

    aux = requests.get('{}/pergunta'.format(servidor))
    aux = json.loads(aux.text)

    if 'winner' in aux:
        jogador['winner'] = json.loads(aux['winner'])
        if jogador['winner']['nick'] == jogador['nick']:
            redirect('/winner')
        redirect('/loser')
    pergunta = aux
    return {'jogador': jogador, 'piadinha': pergunta, 'title': 'Pergunta'}

@app.route('/responder', method='POST')
def verifica_resposta():
    global pergunta
    global jogador

    aux = json.dumps({'resposta': request.forms.get('resposta'), 'id': pergunta['_id']})
    jogador = requests.get('{}/usr/{}/responder/{}'.format(servidor, jogador['nick'], aux))
    jogador = json.loads(jogador.text)
    redirect('/pergunta')

@app.route('/winner', method='GET')
@view('winner.html')
def mostra_winner():
    global jogador
    return {'jogador': jogador['winner'], 'title': 'Um winner'}

@app.route('/winner', method='POST')
def reniciar_jogo():
    global jogador
    aux = requests.get('{}/usr/{}/reiniciar'.format(servidor, jogador['nick']))
    print("Servidor diz:", str(aux.text))
    redirect('/usr/{}'.format(jogador['nick']))

@app.route('/loser', method='GET')
@view('loser.html')
def mostra_loser():
    global jogador
    # t3 = threading.Thread(target=reiniciar_jogo)
    # t3.start()
    return {'jogador': jogador, 'title': 'Um loser'}

@app.route('/loser', method='POST')
@view('loser.html')
def mostra_loser():
    resposta = requests.get('{}/usr/{}/reiniciar'.format(servidor, 'eu sou um coitado'))
    resposta = str(resposta.text).replace('\"', '')
    if resposta == '#partiu':
        print("Servidor diz:", resposta)
        global jogador
        redirect('/usr/{}'.format(jogador['nick']))
    redirect('/loser')
# Tenta uma conexão inicial, para ver se o servidor está ativo
def status_servidor():
    try:
        requests.get('{}/add/{}'.format(servidor, porta))
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
        except requests.exceptions.ConnectionError:
            print("Sem contato com o servidor!!!")
        time.sleep(12)

def situacao_jogo():
    time.sleep(5)
    while True:
        try:
            aux = requests.get('{}/situacaoJogo'.format(servidor))
            aux = str(aux.text).replace('\"', '').split('__')
            if len(aux) == 1:
                print(aux[0] + '\n')
            else:
                for k in aux:
                    if k != '':
                        k = k.split('#')
                        print("Pontos:", k[1] + "\tJogador:", k[0])
        except requests.exceptions.ConnectionError:
            print("Sem contato com o servidor!!!")
        time.sleep(20)

# def reiniciar_jogo():
#     while True:
#         time.sleep(2)
#         resposta = ''
#         try:
#             resposta = requests.get('{}/usr/{}/reiniciar'.format(servidor, 'eu sou um coitado'))
#             resposta = str(resposta.text).replace('\"', '')
#             print("Servidor diz:", resposta)
#         except requests.exceptions.ConnectionError:
#             print("Sem contato com o servidor!!!")
#         if resposta == '#partiu':
#             print("entrooou")
#             break
#     global jogador
#     redirect('/usr/{}'.format(jogador['nick']))

if status_servidor():
    t1 = threading.Thread(target=verificando_servidor)
    t1.start()

    t2 = threading.Thread(target=situacao_jogo)
    t2.start()

run(app, host='localhost', port=porta, debug=True, reloader=True)
# run(app, host='localhost', debug=True, reloader=True)
