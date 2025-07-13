import socket
import json
import time
from threading import Thread

class ServidorTCP:
    def __init__(self, anfitriao='0.0.0.0', porta=12345):
        self.anfitriao = anfitriao
        self.porta = porta
        self.soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soquete_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soquete_servidor.bind((self.anfitriao, self.porta))
        self.soquete_servidor.listen(5)
        
        self.perguntas = self.carregar_perguntas()
        self.pontuacoes = {}
        self.threads_clientes = []
        
    def carregar_perguntas(self):
        with open('../../perguntas/quizPerguntas.json', 'r') as arquivo:
            return json.load(arquivo)
    
    def lidar_com_cliente(self, soquete_cliente, endereco):
        id_cliente = f"{endereco[0]}:{endereco[1]}"
        self.pontuacoes[id_cliente] = 0
        
        for i, pergunta in enumerate(self.perguntas):
            inicio = time.time()
            
            # Envia pergunta
            texto_pergunta = f"Pergunta {i+1}: {pergunta['Pergunta']}\n"
            for opcao in pergunta['Opções']:
                texto_pergunta += f"{opcao}\n"
            soquete_cliente.send(texto_pergunta.encode())
            
            # Recebe resposta
            try:
                resposta = soquete_cliente.recv(1024).decode().strip().upper()
                tempo_resposta = time.time() - inicio

                # Verifica se cliente saiu
                if resposta == "SAIR":
                    print(f"Cliente {id_cliente} saiu do jogo.")
                    break
                
                # Verifica resposta
                if resposta == pergunta['Alternativa correta']:
                    pontuacao = max(1.0 - (0.1 * len([k for k in self.pontuacoes 
                                                      if self.pontuacoes[k] > 0])), 0)
                    self.pontuacoes[id_cliente] += pontuacao
                    retorno = f"Resposta correta! +{pontuacao:.1f} pontos"
                else:
                    retorno = "Resposta incorreta!"
                
                soquete_cliente.send(retorno.encode())
                
                # Envia placar atualizado
                placar = "\nPlacar:\n"
                for jogador, pontuacao in self.pontuacoes.items():
                    placar += f"{jogador}: {pontuacao:.1f}\n"
                soquete_cliente.send(placar.encode())
                
                # Registra tempo de resposta
                print(f"Cliente {id_cliente} - Tempo resposta: {tempo_resposta:.4f}s")
                
            except Exception as erro:
                print(f"Erro com cliente {id_cliente}: {erro}")
                break
        
        # Resultado final
        mensagem_final = "\nJogo encerrado! Resultado final:\n"
        for jogador, pontuacao in self.pontuacoes.items():
            mensagem_final += f"{jogador}: {pontuacao:.1f}\n"
        try:
            soquete_cliente.send(mensagem_final.encode())
        except BrokenPipeError:
            print(f"Cliente {id_cliente} desconectado antes do envio final.")
        soquete_cliente.close()
    
    def iniciar(self):
        print(f"Servidor TCP rodando em {self.anfitriao}:{self.porta}")
        try:
            while True:
                soquete_cliente, endereco = self.soquete_servidor.accept()
                print(f"Conexão estabelecida com {endereco}")
                
                thread_cliente = Thread(target=self.lidar_com_cliente, 
                                        args=(soquete_cliente, endereco))
                thread_cliente.start()
                self.threads_clientes.append(thread_cliente)
                
        except KeyboardInterrupt:
            print("\nEncerrando servidor...")
            for thread in self.threads_clientes:
                thread.join()
            self.soquete_servidor.close()

if __name__ == "__main__":
    servidor = ServidorTCP()
    servidor.iniciar()
