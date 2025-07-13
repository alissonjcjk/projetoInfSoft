import socket
import time

class ClienteTCP:
    def __init__(self, anfitriao_servidor='127.0.0.1', porta_servidor=12345):
        self.anfitriao_servidor = anfitriao_servidor
        self.porta_servidor = porta_servidor
        self.soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def conectar(self):
        self.soquete_cliente.connect((self.anfitriao_servidor, self.porta_servidor))
        print(f"Conectado ao servidor {self.anfitriao_servidor}:{self.porta_servidor}")
        
        try:
            while True:
                # Recebe pergunta
                dados_pergunta = self.soquete_cliente.recv(4096).decode()
                if not dados_pergunta:
                    break
                    
                print(dados_pergunta)
                
                # Simula resposta (na prática seria input do usuário)
                resposta = input("Sua resposta (A/B/C/D): ").upper()
                inicio = time.time()
                self.soquete_cliente.send(resposta.encode())
                
                # Recebe feedback e placar
                retorno = self.soquete_cliente.recv(4096).decode()
                print(retorno)
                
                placar = self.soquete_cliente.recv(4096).decode()
                print(placar)
                
        except Exception as erro:
            print(f"Erro na conexão: {erro}")
        finally:
            self.soquete_cliente.close()

if __name__ == "__main__":
    cliente = ClienteTCP()
    cliente.conectar()
