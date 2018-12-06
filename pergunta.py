import random

class Piadinha:
    def __init__(self, desc, resposta, opcoes, pts):
        self.descricao = desc       # Descrição da pergunta
        self.resposta = resposta    # Resposta correta
        self.opcoes = opcoes        # Array em várias alternativas, incluindo a resposta correta
        self.pontos = pts            # Recompensa por acertar a questao

    def checkResposta(self, r):
        if(r == self.resposta):
            return self.pontos
        return (int(len(self.opcoes) * 0.2) * -1) # Remove pts do usuário

    def obterOpcoes(self):
        random.shuffle(self.opcoes) # Embaralha as opções
        return self.opcoes
