import requests
import bottle
import json
import threading
import time
import sys

peers = sys.argv[1:]

@bottle.route('/estouvivo')
def estou_vivo():
    return json.dumps('Olá')

@bottle.route('/add/<p>')
def index(p):
    # Não adiciona caso já esteja na lista
    if p not in peers:
        peers.append(p)
    return json.dumps(peers)

@bottle.route('/peers')
def index():
    return json.dumps(peers)

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
