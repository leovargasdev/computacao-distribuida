from questao import Piadinha
import requests
import json
import bottle
import threading
import time
import sys

peers = sys.argv[1:]
jogadores = []
questoes =[]
n_questao = 0
vencedor = False
reiniciar = False
questoes.append(Piadinha(0, 'Qual o estado brasileiro que queria ser um carro?', 'Sergipe', ['Parana', 'New York', 'Guatambu', 'São Paulo', 'Gotham City'], 7))
questoes.append(Piadinha(1, 'Por que o anão gosta de surfar na cozinha??', 'Porque tem Microondas', ['Porque hoje é segunda-feira', 'Anão sei', 'Porque ele é um masterchef Júnior'], 13))
questoes.append(Piadinha(2, 'blabla??', 'sadassa', ['sadassa', 'Anão sei', 'Porque ele é um masterchef Júnior'], 1))

# Rota para testar se o servidor está ativo
@bottle.route('/estouvivo')
def estou_vivo():
    return json.dumps('Olar!!')

# Adicionando um novo cliente ao servidor
@bottle.route('/add/<p>')
def index(p):
    if p not in peers: # Não adiciona caso já esteja na lista
        peers.append(p)
    return json.dumps(peers)

# Retorna todos os jogadores e seus respectivos pontos
@bottle.route('/situacaoJogo')
def situacao_jogo():
    global jogadores
    result = ''
    for j in jogadores:
        result += j['nick'] + "#" + str(j['pts']) + "__"
    if result == '':
        return json.dumps('Sem jogadores ativos!!')
    return json.dumps(result)

# Cria um novo jogador, e caso já exita esse nick é retornado suas informações
@bottle.route('/jogador/<nick>')
def retorna_joagador(nick):
    jogador = obterJogador(nick)
    if jogador == False:
        jogador = {'nick': nick, 'pts': 0, 'winner': False}
        jogadores.append(jogador)
        print('Novo jogador criado com sucesso!!')
    return json.dumps(jogador)

# Carrega a próxima pergunta para o jogador
@bottle.route('/pergunta')
def obter_nQuestao():
    global questoes
    global n_questao
    if vencedor:
        return json.dumps({'winner': json.dumps(vencedor)})
    questao = questoes[n_questao]
    questao.embaralhaOpcoes()
    return json.dumps(questao.__dict__)

@bottle.route('/usr/<nick>/responder/<pergunta>')
def verifica_resposta(nick, pergunta):
    global questoes
    global n_questao
    global vencedor

    pergunta = json.loads(pergunta)
    id = int(pergunta['id'])
    pts = questoes[id].checkResposta(pergunta['resposta'])
    jogador = atualizar_pts(nick, pts)

    if pts > 0:
        prox_questao = id + 1
        if prox_questao > n_questao:
            n_questao = prox_questao

    if n_questao == len(questoes):
        if vencedor:
            if jogador['pts'] > vencedor['pts']: # Caso os dois ainda estão na última questão, deve conferir os pontos
                vencedor = jogador
        else: # Não teve vencedor ainda
            vencedor = jogador

    return json.dumps(jogador)

@bottle.route('/usr/<nick>/reiniciar')
def reiniciar_jogo(nick):
    global vencedor
    global jogadores
    global vencedor
    global reiniciar
    global n_questao

    if vencedor:
        if nick == vencedor['nick']:
            print("reiniciando jogo...")
            for j in range(len(jogadores)):
                jogadores[j]['pts'] = 0
            vencedor = False
            reiniciar = False
            n_questao = 0
            return json.dumps('#partiu')
    else:
        return json.dumps('#partiu')
    return json.dumps('Non')

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
                print("[", p, "] Esta ativo?", aux.text)
            except:
                print("[", p, "] Sem contato, faleceu!!!")
        time.sleep(12)

t1 = threading.Thread(target=testar_peers)
t1.start()

bottle.run(host='localhost', port=3000)
