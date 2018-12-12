import sys
import json
import time
import bottle
import requests
import threading
from questao import Piadinha

peers = []
jogadores = []
questoes =[]
n_questao = 0
vencedor = False
semaforo = threading.Semaphore()
questoes.append(Piadinha(0, 'Qual o estado brasileiro que queria ser um carro?', 'Sergipe', ['Parana', 'New York', 'Guatambu', 'São Paulo', 'Gotham City'], 7))
questoes.append(Piadinha(1, 'Por que o anão gosta de surfar na cozinha??', 'Porque tem Microondas', ['Porque hoje é segunda-feira', 'Anão sei', 'Porque ele é um masterchef Júnior'], 13))
questoes.append(Piadinha(2, 'Por que não se deve comprar uma peneira??', 'Pode ser uma furada', ['Você não precisa', 'Porque você não quer peneirar na vida', 'Num sei'], 5))
questoes.append(Piadinha(3, 'Por que a velhinha não usa relógio??', 'Porque ela eh senhora', ['Porque ela é sabia e vê as horas pelo sol', 'Porque o neto robou para comprar um Hot Wheels', 'Porque ela não tem tempo pra isso'], 9))
questoes.append(Piadinha(4, 'Sabe oque o tiaguinho foi fazer na igreja?', 'Foi cantar Pagod', ['Rezar', 'Comungar', 'Fazer um Show', 'Foi cantar "Oh Happy Day"'], 19))
questoes.append(Piadinha(5, 'Por que o policial não lava a louça com sabão?', 'Porque ele prefere deter gente', ['Porque ele não tem tempo', 'Porque sabão é muito liso, e de liso já basta os bandidos', 'Porque não é um sabadão'], 15))
questoes.append(Piadinha(6, 'Sabe porque hoje em dia não se passa mais roupa??', 'Pois a vida passa e a gente nem ve', ['Pessoas não usam mais roupas', 'Pois a única coisa que passa é a uva ou ônibus', 'Porque quem vive de passado é museu'], 21))
questoes.append(Piadinha(7, 'Por que o bombeiro não gosta de andar?', 'Porque ele so corre', ['Pra que andar, se tem uber', 'Porque andar é coisa de véio'], 9))
questoes.append(Piadinha(8, 'Oque é um pontinho pequeno e preto?', 'Eh uma blackteria', ['Um feijão anão', 'O ponto da questão', 'Um ponto negativo', 'Um ponto'], 34))
questoes.append(Piadinha(9, 'E a pergunta que não quer calar, é pavê ou pacume?', 'Todas respostas', ['Pavê', 'Pacume', 'Pacheirar', 'Paolhar'], 50))

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
def obter_pergunta():
    global questoes
    global n_questao
    # Encerra o jogo caso tenha algum vencedor
    if vencedor:
        return json.dumps({'winner': json.dumps(vencedor)})
    questao = questoes[n_questao]
    questao.embaralhaOpcoes()
    return json.dumps(questao.__dict__)

# Verificar a responta do jogador
@bottle.route('/usr/<nick>/responder/<pergunta>')
def verifica_resposta(nick, pergunta):
    global questoes
    global semaforo
    pergunta = json.loads(pergunta)
    id = int(pergunta['id'])
    # [[ INICIO ]]
    semaforo.acquire()
    pts = questoes[id].checkResposta(pergunta['resposta'])
    jogador = atualizar_pts(nick, pts)
    # Caso a responta esteja incorreta os pontos são negativos, logo não tenta avançar a variável global n_questao
    if 0 < pts:
        prox_pergunta(id, jogador)
    semaforo.release()
    # [[ FIM ]]
    return json.dumps(jogador)

@bottle.route('/usr/<nick>/reiniciar')
def reiniciar_jogo(nick):
    global vencedor
    # Quando for reiniciado o vencedor deve estar vazio, podendo assim começar o jogo novamente
    if vencedor == False:
        return json.dumps('#partiu')
    # Somente o vencedor tem o poder de reiniciar o jogo
    if nick == vencedor['nick']:
        reiniciar()
        return json.dumps('#partiu')
    return json.dumps('Non')

# Retorna as informações do jogador
def obterJogador(n):
    global jogadores
    for j in jogadores:
        if j['nick'] == n:
            return j
    return False

# Atualiza a pontuação do jogador
def atualizar_pts(n, pontos):
    global jogadores
    for j in range(len(jogadores)):
        if jogadores[j]['nick'] == n:
            jogadores[j]['pts'] = jogadores[j]['pts'] + pontos
            return jogadores[j]

# Função para avançar a variável global que controla qual será a próxima questão, e também para saber se houve um vencedor
def prox_pergunta(id_pergunta, jogador):
    global n_questao
    global vencedor

    if n_questao < (id_pergunta + 1):
        n_questao = id_pergunta + 1

    if n_questao == len(questoes):
        # Já tem um vencedor, dai tem que conferir os pontos
        if vencedor:
            if jogador['pts'] > vencedor['pts']:
                vencedor = jogador
        # Não teve vencedor ainda
        else:
            vencedor = jogador

# Reseta todas as variáveis globais do server
def reiniciar():
    global vencedor
    global jogadores
    global vencedor
    global n_questao

    for j in range(len(jogadores)):
        jogadores[j]['pts'] = 0
    vencedor = False
    n_questao = 0

# A cada 15 segundos confere se todos os clientes estão ativos
def situacao_clients():
    time.sleep(10)
    while True:
        for p in peers:
            try:
                aux = requests.get('http://localhost:{}/estouvivo'.format(p))
                print("[", p, "] Esta ativo?", aux.text)
            except requests.exceptions.ConnectionError:
                print("[", p, "] Sem contato, faleceu!!!")
        time.sleep(15)

t1 = threading.Thread(target=situacao_clients)
t1.start()

bottle.run(host='localhost', port=3000)
