import socket
import time

class TCPClient:
    def __init__(self, server_host='127.0.0.1', server_port=12345):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self):
        self.client_socket.connect((self.server_host, self.server_port))
        print(f"Conectado ao servidor {self.server_host}:{self.server_port}")
        
        try:
            while True:
                # Recebe pergunta
                question_data = self.client_socket.recv(4096).decode()
                if not question_data:
                    break
                    
                print(question_data)
                
                # Simula resposta (na prática seria input do usuário)
                answer = input("Sua resposta (A/B/C/D): ").upper()
                start_time = time.time()
                self.client_socket.send(answer.encode())
                
                # Recebe feedback e placar
                feedback = self.client_socket.recv(4096).decode()
                print(feedback)
                
                scoreboard = self.client_socket.recv(4096).decode()
                print(scoreboard)
                
        except Exception as e:
            print(f"Erro na conexão: {e}")
        finally:
            self.client_socket.close()

if __name__ == "__main__":
    client = TCPClient()
    client.connect()