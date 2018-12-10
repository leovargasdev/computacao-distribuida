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
questoes.append(zubaluba.Piadinha('Qual o estado brasileiro que queria ser um carro?', 'Sergipe', ['Parana', 'New York', 'Guatambu', 'São Paulo', 'Gotham City'], 7))
questoes.append(zubaluba.Piadinha('Por que o anão gosta de surfar na cozinha??', 'Porque tem Microondas', ['Porque hoje é segunda-feira', 'Anão sei', 'Porque ele é um masterchef Júnior'], 13))
questoes.append(zubaluba.Piadinha('blabla??', 'sadassa', ['sadassa', 'Anão sei', 'Porque ele é um masterchef Júnior'], 1))

@bottle.route('/estouvivo')
def estou_vivo():
    return json.dumps('Olá')

@bottle.route('/add/<p>')
def index(p):
    # Não adiciona caso já esteja na lista
    if p not in peers:
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

@bottle.route('/peers')
def index():
    return json.dumps(peers)

def obterJogador(n):
    global jogadores
    for j in jogadores:
        if j['nick'] == n:
            return j
    return False

def testar_peers():
    time.sleep(10)
    while True:
        for p in peers:
            try:
                aux = requests.get('http://localhost:{}/estouvivo'.format(p))
                print("[", p, "] Está ativo?", aux.text)
            except:
                print("[", p, "] Sem contato, faleceu!!!")
        time.sleep(5)

t1 = threading.Thread(target=testar_peers)
t1.start()

bottle.run(host='localhost', port=3000)
