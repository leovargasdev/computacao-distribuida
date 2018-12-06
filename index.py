import pergunta
import functools
from bottle import Bottle, request, route, jinja2_view, run, response, redirect, static_file, sys

app = Bottle()
view = functools.partial(jinja2_view, template_lookup=['templates'])

porta = int(sys.argv[1])
jogadores = {}
questoes = []
questoes.append(pergunta.Piadinha(
    'Qual o estado brasileiro que queria ser um carro?',
    'Sergipe',
    ['Parana', 'New York', 'Guatambu', 'São Paulo', 'Sergipe', 'Gotham City'],
    7
))
numero_questao = 0
@app.route('/imports/css/<filename>')
def server_static(filename):
    return static_file(filename, root='./imports/css')

# [PÁGINA] Home
@app.route('/')
@view('index.html')
def index():
    return {'title': 'Página Inicial', 'users': ['jogadores', 'topep']}

@app.route('/iniciar', method='POST')
def inicializando_jogador():
    global jogadores
    global porta
    global numero_questao
    nick = request.forms.get('nick')
    if nick:
        if (nick in jogadores) == False:
            jogadores[nick] = 0
            redirect('/usr/{}/pergunta/{}'.format(nick, numero_questao))
    redirect('/')

@app.route('/usr/<nick>/pergunta/<nq>', method='GET')
@view('pergunta.html')
def carregar_pergunta(nick, nq):
    global questoes
    a = questoes[int(nq)].descricao
    return {'nick': nick, 'title': 'Pergunta', 'descricao': a}


run(app, host='localhost', port=porta, debug=True, reloader=True)
