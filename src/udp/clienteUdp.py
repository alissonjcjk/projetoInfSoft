import socket
import time

class UDPClient:
    def __init__(self, server_host='127.0.0.1', server_port=12346):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Configura timeout para recebimento
        self.client_socket.settimeout(5)
        
    def register(self):
        self.client_socket.sendto(b"register", (self.server_host, self.server_port))
        
        try:
            data, _ = self.client_socket.recvfrom(1024)
            print(data.decode())
            return True
        except socket.timeout:
            print("Timeout ao tentar registrar")
            return False
    
    def play(self):
        if not self.register():
            return
            
        try:
            while True:
                # Recebe pergunta
                try:
                    question_data, _ = self.client_socket.recvfrom(4096)
                    print(question_data.decode())
                    
                    # Simula resposta
                    answer = input("Sua resposta (A/B/C/D): ").upper()
                    self.client_socket.sendto(answer.encode(), 
                                           (self.server_host, self.server_port))
                    
                    # Recebe feedback
                    feedback, _ = self.client_socket.recvfrom(4096)
                    print(feedback.decode())
                    
                    # Recebe placar
                    scoreboard, _ = self.client_socket.recvfrom(4096)
                    print(scoreboard.decode())
                
                except socket.timeout:
                    print("Nenhuma pergunta recebida por 5 segundos. Verificando final...")
                    continue
                
        except KeyboardInterrupt:
            print("\nCliente encerrado pelo usuário")
        except Exception as e:
            print(f"Erro durante o jogo: {e}")
        finally:
            self.client_socket.close()

if __name__ == "__main__":
    client = UDPClient()
    client.play()