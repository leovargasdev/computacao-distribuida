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
# jogadores.append({'nome': 'perdi', 'pts': 10})
# jogadores.append({'nome': 'topper', 'pts': 16})
n_questao = 0
vencedor = False

questoes = []
questoes.append(Piadinha(0, 'Qual o estado brasileiro que queria ser um carro?', 'Sergipe', ['Parana', 'New York', 'Guatambu', 'São Paulo', 'Gotham City'], 7))
questoes.append(Piadinha(1, 'Por que o anão gosta de surfar na cozinha??', 'Porque tem Microondas', ['Porque hoje é segunda-feira', 'Anão sei', 'Porque ele é um masterchef Júnior'], 13))
questoes.append(Piadinha(2, 'Por que não se deve comprar uma peneira??', 'Pode ser uma furada', ['Você não precisa', 'Porque você não quer peneirar na vida', 'Num sei'], 5))
# questoes.append(Piadinha(3, 'Por que a velhinha não usa relógio??', 'Porque ela eh senhora', ['Porque ela é sabia e vê as horas pelo sol', 'Porque o neto robou para comprar um Hot Wheels', 'Porque ela não tem tempo pra isso'], 9))
# questoes.append(Piadinha(4, 'Sabe oque o tiaguinho foi fazer na igreja?', 'Foi cantar Pagod', ['Rezar', 'Comungar', 'Fazer um Show', 'Foi cantar "Oh Happy Day"'], 19))
# questoes.append(Piadinha(5, 'Por que o policial não lava a louça com sabão?', 'Porque ele prefere deter gente', ['Porque ele não tem tempo', 'Porque sabão é muito liso, e de liso já basta os bandidos', 'Porque não é um sabadão'], 15))
# questoes.append(Piadinha(6, 'Sabe porque hoje em dia não se passa mais roupa??', 'Pois a vida passa e a gente nem ve', ['Pessoas não usam mais roupas', 'Pois a única coisa que passa é a uva ou ônibus', 'Porque quem vive de passado é museu'], 21))
# questoes.append(Piadinha(7, 'Por que o bombeiro não gosta de andar?', 'Porque ele so corre', ['Pra que andar, se tem uber', 'Porque andar é coisa de véio'], 9))
# questoes.append(Piadinha(8, 'Oque é um pontinho pequeno e preto?', 'Eh uma blackteria', ['Um feijão anão', 'O ponto da questão', 'Um ponto negativo', 'Um ponto'], 34))
# questoes.append(Piadinha(9, 'E a pergunta que não quer calar, é pavê ou pacume?', 'Todas respostas', ['Pavê', 'Pacume', 'Pacheirar', 'Paolhar'], 50))


#   [INICIO]    --> [ [ ROTAS PARA TEMPLATES ] ]

@bottle.route('/')
@view('index.html')
def index():
    global jogadores
    return {'title': 'Página Inicial', 'jogadores': jogadores}

@bottle.route('/iniciar', method='POST')
def carregando_jogador():
    global jogadores
    global jogador
    nome = request.forms.get('nome').replace(' ', '_')
    idJogador = obterJogador(nome)
    if idJogador == -1:
        jogadores.append({'nome': nome, 'pts': 0})
        print("Novo jogador criado!")
        idJogador = len(jogadores) - 1
    jogador = jogadores[idJogador]
    redirect('/pergunta')

@bottle.route('/pergunta', method='GET')
@view('pergunta.html')
def carregar_pergunta():
    global jogador
    global questoes
    global n_questao
    global vencedor
    print ("vencedor:", vencedor)
    if vencedor:
        if vencedor['nome'] == jogador['nome']:
            redirect('/winner')
        redirect('/loser')
    atualiza_nQuestao()
    questao = questoes[n_questao]
    questao.embaralhaOpcoes()

    return {'jogador': jogador, 'piadinha': questao, 'title': 'Pergunta'}

@bottle.route('/responder', method='POST')
def verifica_resposta():
    global n_questao
    global jogador
    global vencedor
    resposta = request.forms.get('resposta')
    pts = questoes[n_questao].checkResposta(resposta)
    jogador['pts'] = jogador['pts'] + pts
    if 0 < pts:
        n_questao = n_questao + 1
        if n_questao == len(questoes):
            atualiza_vencedor(jogador)
    redirect('/pergunta')

@bottle.route('/winner', method='GET')
@view('winner.html')
def mostra_winner():
    global vencedor
    global jogador
    # Caso tenha atualizado o vencedor, redireciona para a rota LOSER
    if vencedor['nome'] != jogador['nome']:
        redirect('/loser')
    return {'jogador': vencedor, 'title': 'Um winner'}

@bottle.route('/loser', method='GET')
@view('loser.html')
def mostra_loser():
    global vencedor
    global jogador
    return {'jogador': jogador, 'vencedor': vencedor, 'title': 'Um loser'}

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

# Retorna o número da questão
@bottle.route('/nPergunta')
def meus_vizinhos():
    global n_questao
    return json.dumps(n_questao)

# Compara os pontos
@bottle.route('/vencedor')
def retorna_possivel_vencedor():
    global vencedor
    if vencedor == False:
        return json.dumps('sem winner')
    return json.dumps(vencedor['nome'])
#   [FIM]       -10-> [ [ ROTAS DE COMUNICAÇÃO ENTRE OS PEERS ] ]


#   [INICIO]    --> [ [ THREADS ] ]
# É verificado se todos os peers(vizinhos) estão ativos
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
# Pergunta-se para todos os peers(vizinhos) conhecidos, a sua respectiva lista de vizinhos
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
# É perguntado a todos os vizinhos suas lista de jogadores
def status_jogadores():
    global peers
    while True:
        for p in peers:
            try:
                jv = requests.get('http://localhost:{}/situacaoJogo'.format(p))
                trata_jogadores_vizinho(jv.text.replace('\"', ''))
            except:
                print("Erro ao obter jogadores do Peer [", p, "]")
        time.sleep(1)
# A cada 15 segundos é perguntado a lista de vizinhos para os seus vizinhos
def vencedor_jogo():
    global peers
    global jogadores
    while True:
        for p in peers:
            try:
                aux = requests.get('http://localhost:{}/vencedor'.format(p))
                aux = str(aux.text).replace('\"', '')
                if aux != 'sem winner':
                    idJogador = obterJogador(aux)
                    atualiza_vencedor(jogadores[idJogador])
            except:
                print("Erro ao comunicar-se com o Peer [", p, "]")
        time.sleep(5)

t1 = threading.Thread(target=situacao_vizinhos)
t1.start()

t2 = threading.Thread(target=novos_vizinhos)
t2.start()

t3 = threading.Thread(target=status_jogadores)
t3.start()

t4 = threading.Thread(target=vencedor_jogo)
t4.start()
#   [FIM]       --> [ [ THREADS ] ]

#   [INICIO]    --> [ [ FUNÇÕES ] ]
# Tenta localizar o jogador e retornar o sua posição no vetor
def obterJogador(n):
    global jogadores
    for j in range(len(jogadores)):
        if jogadores[j]['nome'] == n:
            return j
    return -1
# Recebe todos os jogadores do vizinho e fazendo duas possíveis operações:
#   1ª Adicionado um novo jogador caso ele não se encontra na minha lista
#   2ª Caso o jogador já está na lista, confere se precisa atualizar os pontos dele
def trata_jogadores_vizinho(listaJogadores):
    global jogadores
    if listaJogadores:
        listaJogadores = listaJogadores.split('__')
        for k in listaJogadores:
            [nome, pts] = k.split('#')
            pts = int(pts)
            idJogador = obterJogador(nome)
            # Não localizou nenhum jogador com aquele nome, então ele é adicionado a lista
            if idJogador == -1:
                print("Adicionando novo jogador!")
                jogadores.append({'nome': nome, 'pts': pts})
            # Localizou o jogador, confere se precisa atualizar seus pontos
            else:
                if jogadores[idJogador]['pts'] < pts:
                    print("Atualizando pontos jogador")
                    jogadores[idJogador]['pts'] = pts
# Trata a lista de vizinhos do vizinho(ficou estranha essa frase kk), e caso exista algum vizinho que "eu" não conheça é adicionado na minha lista de vizinhos
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
# Setar/Atualiza o vencedor do jogo
def atualiza_vencedor(pVencedor):
    global vencedor

    if vencedor == False: # Caso não tenha nenhum vencedor
        print("Adicionando vencedor, nome:", pVencedor['nome'])
        vencedor = pVencedor
        print("[if] vencedor:", vencedor)
    else: # Caso já tenha um vencedor nesse client, deve comprar as pontuações
        if vencedor['pts'] < pVencedor['pts']:
            print("Pontos maiores, atualizando vencedor, nome:", pVencedor['nome'])
            vencedor = pVencedor # Atualiza o vencedor se os pontos desse vencedor recebido seja maior
# Confere com todos vizinhos, e pega a questão do vizinho mais avançado nas perguntas
def atualiza_nQuestao():
    global n_questao
    for p in peers:
        try:
            nQuestaoVizinho = requests.get('http://localhost:{}/nPergunta'.format(p))
            nQuestaoVizinho = int(nQuestaoVizinho.text)
            if n_questao < nQuestaoVizinho:
                print("Vizinho está mais avançado!!")
                n_questao = nQuestaoVizinho
        except:
            print("Erro ao obter n_questao do Peer [", p, "]")
#   [FIM]       --> [ [ FUNÇÕES ] ]

# Carregando CSS
@bottle.route('/imports/css/<filename>')
def server_static(filename):
    return static_file(filename, root='./imports/css')

bottle.run(host='localhost', port=int(port))
