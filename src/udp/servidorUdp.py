import socket
import json
import time
from threading import Thread

class ServidorUDP:
    def __init__(self, anfitriao='0.0.0.0', porta=12346):
        self.anfitriao = anfitriao
        self.porta = porta
        self.soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soquete_servidor.bind((self.anfitriao, self.porta))
        
        self.perguntas = self.carregar_perguntas()
        self.pontuacoes = {}
        self.enderecos_clientes = []
        self.tempos_resposta = {}
        
    def carregar_perguntas(self):
        with open('../../perguntas/quizPerguntas.json', 'r') as arquivo:
            return json.load(arquivo)
    
    def enviar_pergunta(self, pergunta, numero_pergunta):
        texto_pergunta = f"Pergunta {numero_pergunta}: {pergunta['Pergunta']}\n"
        for opcao in pergunta["Opções"]:
            texto_pergunta += f"{opcao}\n"
        
        for endereco in self.enderecos_clientes:
            self.soquete_servidor.sendto(texto_pergunta.encode(), endereco)
    
    def atualizar_placar(self):
        placar = "\nPlacar:\n"
        for jogador, pontuacao in self.pontuacoes.items():
            placar += f"{jogador}: {pontuacao:.1f}\n"
        
        for endereco in self.enderecos_clientes:
            self.soquete_servidor.sendto(placar.encode(), endereco)
    
    def tratar_respostas(self, pergunta, numero_pergunta):
        respostas_corretas = 0
        respostas = {}
        inicio_pergunta = time.time()
        
        # Tempo limite para respostas (10 segundos)
        while time.time() - inicio_pergunta < 10 and len(respostas) < len(self.enderecos_clientes):
            try:
                self.soquete_servidor.settimeout(1)
                dados, endereco = self.soquete_servidor.recvfrom(1024)
                resposta = dados.decode().strip().upper()
                
                if endereco not in respostas:
                    tempo_resposta = time.time() - inicio_pergunta
                    self.tempos_resposta[endereco] = tempo_resposta
                    respostas[endereco] = resposta
                    
                    if resposta == pergunta['Alternativa correta']:
                        respostas_corretas += 1
                        pontuacao = max(1.0 - (0.1 * (respostas_corretas - 1)), 0)
                        id_cliente = f"{endereco[0]}:{endereco[1]}"
                        self.pontuacoes[id_cliente] = self.pontuacoes.get(id_cliente, 0) + pontuacao
                        retorno = f"Resposta correta! +{pontuacao:.1f} pontos"
                    else:
                        retorno = "Resposta incorreta!"
                    
                    self.soquete_servidor.sendto(retorno.encode(), endereco)
            
            except socket.timeout:
                continue
        
        self.atualizar_placar()
    
    def iniciar(self):
        print(f"Servidor UDP rodando em {self.anfitriao}:{self.porta}")
        
        # Registrar clientes
        print("Aguardando clientes se registrarem...")
        while len(self.enderecos_clientes) < 1:  # Altere conforme o número desejado de clientes
            try:
                dados, endereco = self.soquete_servidor.recvfrom(1024)
                if endereco not in self.enderecos_clientes:
                    self.enderecos_clientes.append(endereco)
                    id_cliente = f"{endereco[0]}:{endereco[1]}"
                    self.pontuacoes[id_cliente] = 0
                    print(f"Cliente registrado: {id_cliente}")
                    self.soquete_servidor.sendto("Registrado com sucesso!".encode(), endereco)
            except Exception as erro:
                print(f"Erro no registro: {erro}")
        
        # Iniciar quiz
        for i, pergunta in enumerate(self.perguntas):
            print(f"Enviando pergunta {i+1}")
            self.enviar_pergunta(pergunta, i+1)
            self.tratar_respostas(pergunta, i+1)
        
        # Final do jogo
        mensagem_final = "\nJogo encerrado! Resultado final:\n"
        for jogador, pontuacao in self.pontuacoes.items():
            mensagem_final += f"{jogador}: {pontuacao:.1f}\n"
        
        # Adicionar tempos de resposta
        mensagem_final += "\nTempos de resposta:\n"
        for endereco, tempo in self.tempos_resposta.items():
            id_cliente = f"{endereco[0]}:{endereco[1]}"
            mensagem_final += f"{id_cliente}: {tempo:.4f}s\n"
        
        for endereco in self.enderecos_clientes:
            self.soquete_servidor.sendto(mensagem_final.encode(), endereco)
        
        print("Jogo encerrado. Servidor finalizado.")

if __name__ == "__main__":
    servidor = ServidorUDP()
    servidor.iniciar()
