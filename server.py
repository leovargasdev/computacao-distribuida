import zubaluba
import requests
import bottle
import json
import threading
import time
import sys

peers = sys.argv[1:]
jogadores = []
n_questao = 0
questoes = []
questoes.append(zubaluba.Piadinha(0, 'Qual o estado brasileiro que queria ser um carro?', 'Sergipe', ['Parana', 'New York', 'Guatambu', 'São Paulo', 'Gotham City'], 7))
questoes.append(zubaluba.Piadinha(1, 'Por que o anão gosta de surfar na cozinha??', 'Porque tem Microondas', ['Porque hoje é segunda-feira', 'Anão sei', 'Porque ele é um masterchef Júnior'], 13))
questoes.append(zubaluba.Piadinha(2, 'blabla??', 'sadassa', ['sadassa', 'Anão sei', 'Porque ele é um masterchef Júnior'], 1))

@bottle.route('/estouvivo')
def estou_vivo():
    return json.dumps('Olá')

@bottle.route('/add/<p>')
def index(p):
    if p not in peers: # Não adiciona caso já esteja na lista
        peers.append(p)
    return json.dumps(peers)

@bottle.route('/jogador/<nick>')
def retorna_joagador(nick):
    jogador = obterJogador(nick)
    if jogador == False:
        jogador = {'nick': nick, 'pts': 0}
        jogadores.append(jogador)
        print('Novo jogador criado com sucesso!!')
    return json.dumps(jogador)

@bottle.route('/pergunta')
def obter_nQuestao():
    global questoes
    global n_questao

    questao = questoes[n_questao]
    questao.embaralhaOpcoes()

    return json.dumps(questao.__dict__)

@bottle.route('/usr/<nick>/responder/<pergunta>')
def verifica_resposta(nick, pergunta):
    global questoes
    pergunta = json.loads(pergunta)
    id = int(pergunta['id'])
    pts = questoes[id].checkResposta(pergunta['resposta'])

    if pts > 0:
        prox_questao = id + 1
        if prox_questao > n_questao:
            n_questao = prox_questao

    print("nick:", pts)
    jogador = atualizar_pts(nick, pts)
    print("jogador:", jogador)
    return json.dumps(jogador)

@bottle.route('/peers')
def index():
    return json.dumps(peers)

def obterJogador(n):
    global jogadores
    for j in jogadores:
        if j['nick'] == n:
            return j
    return False

def atualizar_pts(n, pontos):
    global jogadores
    for j in range(len(jogadores)):
        if jogadores[j]['nick'] == n:
            jogadores[j]['pts'] = jogadores[j]['pts'] + pontos
            return jogadores[j]

def testar_peers():
    time.sleep(10)
    while True:
        for p in peers:
            try:
                aux = requests.get('http://localhost:{}/estouvivo'.format(p))
                print("[", p, "] Está ativo?", aux.text)
            except:
                print("[", p, "] Sem contato, faleceu!!!")
        time.sleep(8)

t1 = threading.Thread(target=testar_peers)
t1.start()

bottle.run(host='localhost', port=3000)
