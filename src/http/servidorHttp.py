import socket
import json
from threading import Thread

class HTTPServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        self.questions = self.load_questions()
        self.scores = {}

    def load_questions(self):
        with open('../perguntas/quizPerguntas.json', 'r') as f:
            return json.load(f)

    def create_http_response(self, status, content, content_type='text/plain'):
        response = f"HTTP/1.1 {status}\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {len(content)}\r\n"
        response += "Connection: close\r\n\r\n"
        response += content
        return response

    def handle_request(self, client_socket):
        try:
            request = client_socket.recv(4096).decode()
            
            if not request:
                return

            # Pega o método HTTP (simplificado)
            method = request.split(' ')[0]
            path = request.split(' ')[1]

            if method == 'GET' and path == '/question':
                question = self.questions[0]  # Simplificado - deveria controlar o estado
                content = json.dumps({
                    'question': question['question'],
                    'options': question['options']
                })
                response = self.create_http_response('200 OK', content, 'application/json')
            
            elif method == 'POST' and path == '/answer':
                content_length = int(request.split('Content-Length: ')[1].split('\r\n')[0])
                post_data = request.split('\r\n\r\n')[1][:content_length]
                
                answer_data = json.loads(post_data)
                # Lógica de verificação de resposta aqui
                response = self.create_http_response('200 OK', '{"correct": true}', 'application/json')
            
            else:
                response = self.create_http_response('404 Not Found', 'Endpoint not found')

            client_socket.sendall(response.encode())

        except Exception as e:
            print(f"Error handling request: {e}")
            error_response = self.create_http_response('500 Internal Server Error', 'Server error')
            client_socket.sendall(error_response.encode())
        finally:
            client_socket.close()

    def start(self):
        print(f"HTTP Server running on {self.host}:{self.port}")
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                Thread(target=self.handle_request, args=(client_socket,)).start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.server_socket.close()

if __name__ == "__main__":
    server = HTTPServer()
    server.start()