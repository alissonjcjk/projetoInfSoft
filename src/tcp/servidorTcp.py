import socket
import json
import time
from threading import Thread

class TCPServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        self.questions = self.load_questions()
        self.scores = {}
        self.client_threads = []
        
    def load_questions(self):
        with open('/home/CIN/asb3/projetoInfSoft/perguntas/quizPerguntas.json', 'r') as f:
            return json.load(f)
    
    def handle_client(self, client_socket, address):
        client_id = f"{address[0]}:{address[1]}"
        self.scores[client_id] = 0
        
        for i, question in enumerate(self.questions):
            start_time = time.time()
            
            # Envia pergunta
            question_str = f"Pergunta {i+1}: {question['question']}\n"
            for option in question['options']:
                question_str += f"{option}\n"
            client_socket.send(question_str.encode())
            
            # Recebe resposta
            try:
                answer = client_socket.recv(1024).decode().strip().upper()
                response_time = time.time() - start_time
                
                # Verifica resposta
                if answer == question['correct_answer']:
                    score = max(1.0 - (0.1 * len([k for k in self.scores 
                                                 if self.scores[k] > 0])), 0)
                    self.scores[client_id] += score
                    feedback = f"Resposta correta! +{score:.1f} pontos"
                else:
                    feedback = "Resposta incorreta!"
                
                client_socket.send(feedback.encode())
                
                # Envia placar atualizado
                scoreboard = "\nPlacar:\n"
                for player, score in self.scores.items():
                    scoreboard += f"{player}: {score:.1f}\n"
                client_socket.send(scoreboard.encode())
                
                # Registra tempo de resposta
                print(f"Cliente {client_id} - Tempo resposta: {response_time:.4f}s")
                
            except Exception as e:
                print(f"Erro com cliente {client_id}: {e}")
                break
        
        # Resultado final
        final_msg = "\nJogo encerrado! Resultado final:\n"
        for player, score in self.scores.items():
            final_msg += f"{player}: {score:.1f}\n"
        client_socket.send(final_msg.encode())
        client_socket.close()
    
    def start(self):
        print(f"Servidor TCP rodando em {self.host}:{self.port}")
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"Conexão estabelecida com {address}")
                
                client_thread = Thread(target=self.handle_client, 
                                     args=(client_socket, address))
                client_thread.start()
                self.client_threads.append(client_thread)
                
        except KeyboardInterrupt:
            print("\nEncerrando servidor...")
            for thread in self.client_threads:
                thread.join()
            self.server_socket.close()

if __name__ == "__main__":
    server = TCPServer()
    server.start()