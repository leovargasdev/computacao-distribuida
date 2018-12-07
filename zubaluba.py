import random

class Piadinha:
    def __init__(self, desc, resposta, opcoes, pts):
        self.descricao = desc           # Descrição da pergunta
        self.resposta = resposta        # Resposta correta
        self.opcoes = opcoes            # Array em várias alternativas
        self.opcoes.append(resposta)    # incluindo a resposta correta
        self.pontos = pts               # Recompensa por acertar a questao

    def checkResposta(self, r):
        if(r == self.resposta):
            return self.pontos
        return (int(len(self.opcoes) * 0.2) * -1) # Remove pts do usuário

    def embaralhaOpcoes(self):
        random.shuffle(self.opcoes) # Embaralha as opções

class User:
    def __init__(self, id, nick):
        self._id = id
        self.nick = nick
        self.pontos = 0
