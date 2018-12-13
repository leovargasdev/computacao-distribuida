import sys
import json
import time
import bottle
import requests
import functools
import threading
from questao import Piadinha
from bottle import Bottle, route, request, jinja2_view, run, response, redirect, static_file

view = functools.partial(jinja2_view, template_lookup=['templates'])

peers = set(sys.argv[2:])
port = sys.argv[1]

jogador = ''
jogadores = []
jogadores.append({'pts': 1090, 'nome': 'Perdi'})
jogadores.append({'pts': 100, 'nome': 'Teste'})
jogadores.append({'pts': 100, 'nome': 'TOpper'})
n_questao = 0
vencedor = False
semaforo = threading.Semaphore()

questoes = []
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


#   [INICIO]    --> [ [ ROTAS PARA TEMPLATES ] ]

@bottle.route('/')
@view('index.html')
def index():
    global jogadores
    return {'title': 'Página Inicial', 'jogadores': jogadores}

#   [FIM]       --> [ [ ROTAS PARA TEMPLATES ] ]







#   [INICIO]    --> [ [ ROTAS DE COMUNICAÇÃO ENTRE OS PEERS ] ]

# Rota para testar se o servidor está ativo
@bottle.route('/estouvivo')
def estou_vivo():
    return json.dumps('Olar!!')

# Rota para retornar os vizinhos conhecidos
@bottle.route('/meusVizinhos')
def meus_vizinhos():
    global peers
    return json.dumps(list(peers))

# Retorna todos os jogadores e seus respectivos pontos
@bottle.route('/situacaoJogo')
def situacao_jogo():
    global jogadores
    result = ''
    for j in jogadores:
        result += j['nome'] + "#" + str(j['pts']) + "__"
    if result:
        return json.dumps(result[:-2])
    return json.dumps(result)

#   [FIM]       --> [ [ ROTAS DE COMUNICAÇÃO ENTRE OS PEERS ] ]


#   [INICIO]    --> [ [ THREADS ] ]

# A cada 15 segundos confere se todos os clientes estão ativos
def situacao_vizinhos():
    global peers
    time.sleep(5)
    while True:
        for p in peers:
            try:
                aux = requests.get('http://localhost:{}/estouvivo'.format(p))
                # print("[", p, "] Esta ativo?", aux.text)
            except requests.exceptions.ConnectionError:
                print("[", p, "] Sem contato, faleceu!!!")
        time.sleep(5)

def cria_vetor_vizinhos(msg):
    global port
    result = msg.replace('\"', '')
    result = result.replace('[', '')
    result = result.replace(']', '')
    result = result.replace(' ', '')
    result = set(result.split(','))
    if port in result:
        result.remove(port)
    return result

# A cada 15 segundos é perguntado a lista de vizinhos para os seus vizinhos
def novos_vizinhos():
    global peers
    time.sleep(5)
    while True:
        vizinhosNovos = []
        for p in peers:
            try:
                aux = requests.get('http://localhost:{}/meusVizinhos'.format(p))
                vizinhosNovos = cria_vetor_vizinhos(aux.text) # vv: vizinhos dos vizinhos
            except requests.exceptions.ConnectionError:
                continue
        peers = peers.union(vizinhosNovos)
        time.sleep(10)

def trata_jogadores_vizinho(listaJogadores):
    global jogadores
    if listaJogadores:
        listaJogadores = listaJogadores.split('__')
        for k in listaJogadores:
            novo = True
            [nome, pts] = k.split('#')
            pts = int(pts)
            for j in range(len(jogadores)):
                if jogadores[j]['nome'] == nome:
                    novo = False
                    if jogadores[j]['pts'] < pts:
                        print("Atualizando pontos jogador")
                        jogadores[j]['pts'] = int(pts)
                    break
            # Adicionar novo jogador
            if novo:
                print("Adicionando novo jogador!")
                jogadores.append({'nome': nome, 'pts': pts})



# A cada 15 segundos é perguntado a lista de vizinhos para os seus vizinhos
def status_jogadores():
    global peers
    time.sleep(10)
    while True:
        for p in peers:
            try:
                jv = requests.get('http://localhost:{}/situacaoJogo'.format(p))
                trata_jogadores_vizinho(jv.text.replace('\"', ''))
            except:
                print("Erro ao obter jogadores do Peer [", p, "]")
        time.sleep(10)

# t1 = threading.Thread(target=situacao_vizinhos)
# t1.start()
#
# t2 = threading.Thread(target=novos_vizinhos)
# t2.start()

t3 = threading.Thread(target=status_jogadores)
t3.start()

#   [FIM]       --> [ [ THREADS ] ]

# Carregando CSS
@bottle.route('/imports/css/<filename>')
def server_static(filename):
    return static_file(filename, root='./imports/css')

bottle.run(host='localhost', port=int(port))
