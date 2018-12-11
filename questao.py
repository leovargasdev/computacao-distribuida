import random

class Piadinha:
    def __init__(self, id, desc, resposta, opcoes, pts):
        self._id = id                   # Esse id é incremental
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
