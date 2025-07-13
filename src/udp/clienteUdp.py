import socket
import time

class ClienteUDP:
    def __init__(self, anfitriao_servidor='127.0.0.1', porta_servidor=12346):
        self.anfitriao_servidor = anfitriao_servidor
        self.porta_servidor = porta_servidor
        self.soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Configura timeout para recebimento
        self.soquete_cliente.settimeout(5)
        
    def registrar(self):
        self.soquete_cliente.sendto(b"registrar", (self.anfitriao_servidor, self.porta_servidor))
        
        try:
            dados, _ = self.soquete_cliente.recvfrom(1024)
            print(dados.decode())
            return True
        except socket.timeout:
            print("Tempo esgotado ao tentar registrar")
            return False
    
    def jogar(self):
        if not self.registrar():
            return
            
        try:
            while True:
                # Recebe pergunta
                try:
                    dados_pergunta, _ = self.soquete_cliente.recvfrom(4096)
                    print(dados_pergunta.decode())
                    
                    # Simula resposta
                    resposta = input("Sua resposta (A/B/C/D): ").upper()
                    self.soquete_cliente.sendto(resposta.encode(), 
                                                (self.anfitriao_servidor, self.porta_servidor))
                    
                    # Recebe feedback
                    retorno, _ = self.soquete_cliente.recvfrom(4096)
                    print(retorno.decode())
                    
                    # Recebe placar
                    placar, _ = self.soquete_cliente.recvfrom(4096)
                    print(placar.decode())
                
                except socket.timeout:
                    print("Nenhuma pergunta recebida por 5 segundos. Verificando final...")
                    continue
                
        except KeyboardInterrupt:
            print("\nCliente encerrado pelo usuário")
        except Exception as erro:
            print(f"Erro durante o jogo: {erro}")
        finally:
            self.soquete_cliente.close()

if __name__ == "__main__":
    cliente = ClienteUDP()
    cliente.jogar()
