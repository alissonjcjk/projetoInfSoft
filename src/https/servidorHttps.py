import socket
import ssl
import json
from threading import Thread, Lock
import os

class HTTPSServer:
    def __init__(self, host='0.0.0.0', port=8443):
        self.host = host
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind((self.host, self.port))
        self.tcp_socket.listen(5)
        
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain('../../cert/certificate.pem', '../../cert/key.pem')
        
        self.questions = self.load_questions()
        self.current_question = 0
        self.scores = {}
        self.lock = Lock()
        self.quiz_active = True

    def load_questions(self):
        with open('../../perguntas/quizPerguntas.json', 'r') as f:
            return json.load(f)

    def create_response(self, status, content, content_type='application/json'):
        response = f"HTTP/1.1 {status}\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {len(content)}\r\n"
        response += "Connection: close\r\n\r\n"
        response += content
        return response

    def handle_request(self, ssl_socket):
        try:
            if not self.quiz_active:
                response = self.create_response('200 OK', json.dumps({'status': 'error', 'message': 'Quiz completed'}))
                ssl_socket.sendall(response.encode())
                return

            request = ssl_socket.recv(4096).decode()
            if not request:
                return

            headers = request.split('\r\n')
            first_line = headers[0].split()
            if len(first_line) < 3:
                return
                
            method, path, _ = first_line
            response_data = {}
            
            if method == 'GET' and path == '/question':
                if self.current_question >= len(self.questions):
                    self.quiz_active = False
                    response_data = {
                        'status': 'completed',
                        'message': 'Quiz finished',
                        'final_score': 0  # Será atualizado pelo IP do cliente
                    }
                else:
                    question = self.questions[self.current_question]
                    response_data = {
                        'status': 'success',
                        'question_number': self.current_question + 1,
                        'total_questions': len(self.questions),
                        'question': question['Pergunta'],
                        'options': question['Opções'],
                        'is_last': (self.current_question + 1 == len(self.questions))
                    }
            
            elif method == 'POST' and path == '/answer':
                content_length = 0
                for header in headers:
                    if 'Content-Length:' in header:
                        content_length = int(header.split(': ')[1])
                        break
                
                body = request.split('\r\n\r\n')[1][:content_length]
                answer_data = json.loads(body)
                
                question = self.questions[self.current_question]
                is_correct = answer_data.get('answer', '').upper() == question['Alternativa correta']
                
                client_id = ssl_socket.getpeername()[0]  # Usa IP como identificador
                with self.lock:
                    if is_correct:
                        self.scores[client_id] = self.scores.get(client_id, 0) + 1
                
                is_last = (self.current_question + 1 == len(self.questions))
                response_data = {
                    'status': 'answered',
                    'correct': is_correct,
                    'correct_answer': question['Alternativa correta'],
                    'score': self.scores.get(client_id, 0),
                    'quiz_completed': is_last
                }
                
                if not is_last:
                    self.current_question += 1
                else:
                    self.quiz_active = False
            
            else:
                response_data = {'status': 'error', 'message': 'Invalid endpoint'}
            
            response = self.create_response('200 OK', json.dumps(response_data))
            ssl_socket.sendall(response.encode())
            
        except Exception as e:
            print(f"Error handling request: {str(e)}")
            error_response = self.create_response('500 Internal Server Error', json.dumps({'status': 'error', 'message': str(e)}))
            ssl_socket.sendall(error_response.encode())
        finally:
            ssl_socket.close()

    def start(self):
        print(f"HTTPS Server running on {self.host}:{self.port}")
        try:
            while self.quiz_active:
                client_socket, addr = self.tcp_socket.accept()
                try:
                    ssl_socket = self.context.wrap_socket(client_socket, server_side=True)
                    Thread(target=self.handle_request, args=(ssl_socket,)).start()
                except ssl.SSLError as e:
                    print(f"SSL Error: {e}")
                    client_socket.close()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.tcp_socket.close()
            print("Server stopped")

if __name__ == "__main__":
    server = HTTPSServer()
    server.start()