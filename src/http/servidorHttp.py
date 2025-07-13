import socket
import json
from threading import Thread, Lock

class HTTPServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        self.questions = self.load_questions()
        self.current_question = 0
        self.scores = {}
        self.lock = Lock()  # Para controle de concorrência

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
    def handle_request(self, client_socket, client_address):
        try:
            request = client_socket.recv(4096).decode()
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
                    response_data = {
                        'status': 'completed',
                        'message': 'Quiz finished',
                        'final_score': self.scores.get(client_address[0], 0)
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
                
                client_id = client_address[0]
                if is_correct:
                    self.scores[client_id] = self.scores.get(client_id, 0) + 1
                
                # Determina se esta era a última pergunta ANTES de incrementar
                is_last_question = (self.current_question + 1 == len(self.questions))
                
                response_data = {
                    'status': 'answered',
                    'correct': is_correct,
                    'correct_answer': question['Alternativa correta'],
                    'score': self.scores.get(client_id, 0),
                    'quiz_completed': is_last_question
                }
                
                # Avança somente se não for a última pergunta
                if not is_last_question:
                    self.current_question += 1
                
            else:
                response_data = {'status': 'error', 'message': 'Invalid endpoint'}
            
            response = self.create_response('200 OK', json.dumps(response_data))
            client_socket.sendall(response.encode())
            
        except Exception as e:
            print(f"Error handling request: {str(e)}")
            error_response = self.create_response('500 Internal Server Error', json.dumps({'status': 'error', 'message': str(e)}))
            client_socket.sendall(error_response.encode())
        finally:
            client_socket.close()

    def start(self):
        print(f"HTTP Server running on {self.host}:{self.port}")
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                Thread(target=self.handle_request, args=(client_socket, addr)).start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.server_socket.close()

if __name__ == "__main__":
    server = HTTPServer()
    server.start()