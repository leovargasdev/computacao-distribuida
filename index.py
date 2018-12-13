import sys
import json
import time
import bottle
import requests
import threading
from questao import Piadinha

peers = set(sys.argv[2:])
port = sys.argv[1]
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

# Rota para retornar os vizinhos conhecidos
@bottle.route('/meusVizinhos')
def estou_vivo():
    global peers
    return json.dumps(list(peers))

# A cada 15 segundos confere se todos os clientes estão ativos
def situacao_vizinhos():
    global peers
    while True:
        for p in peers:
            try:
                aux = requests.get('http://localhost:{}/estouvivo'.format(p))
                print("[", p, "] Esta ativo?", aux.text)
            except requests.exceptions.ConnectionError:
                print("[", p, "] Sem contato, faleceu!!!")
        time.sleep(5)

# A cada 15 segundos é perguntado a lista de vizinhos para os seus vizinhos
def novos_vizinhos():
    global peers
    while True:
        vizinhosNovos = []
        for p in peers:
            try:
                aux = requests.get('http://localhost:{}/meusVizinhos'.format(p))
                vizinhosNovos = cria_vetor_vizinhos(aux.text) # vv: vizinhos dos vizinhos
                # print("[", p, "] vizinhos:", vizinhosNovos)
            except requests.exceptions.ConnectionError:
                continue
        peers = peers.union(vizinhosNovos)
        time.sleep(10)
        print("meus peers:", peers)

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

t1 = threading.Thread(target=situacao_vizinhos)
t1.start()

t2 = threading.Thread(target=novos_vizinhos)
t2.start()

bottle.run(host='localhost', port=int(port))
