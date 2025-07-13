import socket
import json
import time
from threading import Thread

class UDPServer:
    def __init__(self, host='0.0.0.0', port=12346):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        
        self.questions = self.carregarPerguntas()
        self.scores = {}
        self.client_addresses = []
        self.response_times = {}
        
    def carregarPerguntas(self):
        with open('/Users/aliss/projetoInfSoft/perguntas/quizPerguntas.json', 'r') as f:
            return json.load(f)
    
    def broadcast_question(self, question, question_num):
        question_str = f"Pergunta {question_num}: {question['Pergunta']}\n"
        for option in question["Opcoes"]:
            question_str += f"{option}\n"
        
        for address in self.client_addresses:
            self.server_socket.sendto(question_str.encode(), address)
    
    def update_scoreboard(self):
        scoreboard = "\nPlacar:\n"
        for player, score in self.scores.items():
            scoreboard += f"{player}: {score:.1f}\n"
        
        for address in self.client_addresses:
            self.server_socket.sendto(scoreboard.encode(), address)
    
    def handle_responses(self, question, question_num):
        correct_answers = 0
        responses = {}
        question_start = time.time()
        
        # Tempo limite para respostas (10 segundos)
        while time.time() - question_start < 10 and len(responses) < len(self.client_addresses):
            try:
                self.server_socket.settimeout(1)
                data, address = self.server_socket.recvfrom(1024)
                answer = data.decode().strip().upper()
                
                if address not in responses:
                    response_time = time.time() - question_start
                    self.response_times[address] = response_time
                    responses[address] = answer
                    
                    if answer == question['Alternativa correta']:
                        correct_answers += 1
                        score = max(1.0 - (0.1 * (correct_answers - 1)), 0)
                        client_id = f"{address[0]}:{address[1]}"
                        self.scores[client_id] = self.scores.get(client_id, 0) + score
                        feedback = f"Resposta correta! +{score:.1f} pontos"
                    else:
                        feedback = "Resposta incorreta!"
                    
                    self.server_socket.sendto(feedback.encode(), address)
            
            except socket.timeout:
                continue
        
        self.update_scoreboard()
    
    def start(self):
        print(f"Servidor UDP rodando em {self.host}:{self.port}")
        
        # Registra clientes
        print("Aguardando clientes se registrarem...")
        while len(self.client_addresses) < 1:  # Mude para o número desejado de clientes
            try:
                data, address = self.server_socket.recvfrom(1024)
                if address not in self.client_addresses:
                    self.client_addresses.append(address)
                    client_id = f"{address[0]}:{address[1]}"
                    self.scores[client_id] = 0
                    print(f"Cliente registrado: {client_id}")
                    self.server_socket.sendto("Registrado com sucesso!".encode(), address)
            except Exception as e:
                print(f"Erro no registro: {e}")
        
        # Inicia o quiz
        for i, question in enumerate(self.questions):
            print(f"Enviando pergunta {i+1}")
            self.broadcast_question(question, i+1)
            self.handle_responses(question, i+1)
        
        # Final do jogo
        final_msg = "\nJogo encerrado! Resultado final:\n"
        for player, score in self.scores.items():
            final_msg += f"{player}: {score:.1f}\n"
        
        # Adiciona tempos de resposta
        final_msg += "\nTempos de resposta:\n"
        for address, resp_time in self.response_times.items():
            client_id = f"{address[0]}:{address[1]}"
            final_msg += f"{client_id}: {resp_time:.4f}s\n"
        
        for address in self.client_addresses:
            self.server_socket.sendto(final_msg.encode(), address)
        
        print("Jogo encerrado. Servidor finalizado.")

if __name__ == "__main__":
    server = UDPServer()
    server.start()