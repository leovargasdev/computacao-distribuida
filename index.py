import zubaluba
import functools
from bottle import Bottle, request, route, jinja2_view, run, response, redirect, static_file, sys

app = Bottle()
view = functools.partial(jinja2_view, template_lookup=['templates'])
porta = int(sys.argv[1])

jogadores = []
questoes = []
n_questao = 0
questoes.append(zubaluba.Piadinha('Qual o estado brasileiro que queria ser um carro?', 'Sergipe', ['Parana', 'New York', 'Guatambu', 'São Paulo', 'Gotham City'], 7))

questoes.append(zubaluba.Piadinha('Por que o anão gosta de surfar na cozinha??', 'Porque tem Microondas', ['Porque hoje é segunda-feira', 'Anão sei', 'Porque ele é um masterchef Júnior'], 13))

questoes.append(zubaluba.Piadinha('blabla??', 'sadassa', ['sadassa', 'Anão sei', 'Porque ele é um masterchef Júnior'], 1))

@app.route('/imports/css/<filename>')
def server_static(filename):
    return static_file(filename, root='./imports/css')

@app.route('/')
@view('index.html')
def index():
    global jogadores
    return {'title': 'Página Inicial', 'users': jogadores}

# Criar um novo jogador
@app.route('/iniciar', method='POST')
def inicializando_jogador():

    global jogadores
    global n_questao

    id_jogador = int(len(jogadores))
    nick = request.forms.get('nick')

    if obterJogador(nick) == False:
        jogadores.append(zubaluba.User(id_jogador, nick))
        redirect('/usr/{}/pergunta'.format(nick))

    redirect('/')

@app.route('/usr/<nick>/pergunta', method='GET')
@view('pergunta.html')
def carregar_pergunta(nick):
    global questoes
    global n_questao

    if n_questao == len(questoes):
        redirect('/winner/{}'.format(nick))

    questao = questoes[n_questao]
    questao.embaralhaOpcoes()

    return {'jogador': obterJogador(nick), 'piadinha': questao, 'numero': n_questao, 'title': 'Pergunta'}

@app.route('/usr/<nick>/responder/<nq>', method='POST')
def verifica_resposta(nick, nq):
    global questoes
    global jogadores
    global n_questao

    id = obterJogador(nick)._id
    resposta = request.forms.get('resposta')

    pts = questoes[int(nq)].checkResposta(resposta)
    jogadores[id].pontos = pts + jogadores[id].pontos

    if pts > 0:
        nq = int(nq) + 1
        if nq > n_questao:
            n_questao = nq

    redirect('/usr/{}/pergunta'.format(jogadores[id].nick))

@app.route('/winner/<nick>', method='GET')
@view('winner.html')
def verifica_resposta(nick):
    return {'jogador': obterJogador(nick), 'title': 'Um winner'}

def obterJogador(n):
    global jogadores
    for j in jogadores:
        if j.nick == n:
            return j
    return False


run(app, host='localhost', port=porta, debug=True, reloader=True)
