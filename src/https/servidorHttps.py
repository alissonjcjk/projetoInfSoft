import socket
import ssl
import json
from threading import Thread

class HTTPSServer:
    def __init__(self, host='0.0.0.0', port=8443):
        self.host = host
        self.port = port
        
        # Configuração do socket TCP básico
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind((self.host, self.port))
        self.tcp_socket.listen(5)
        
        # Configuração SSL
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain('cert/certificate.pem', 'cert/key.pem')
        
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

    def handle_request(self, ssl_socket):
        try:
            request = ssl_socket.recv(4096).decode()
            
            # Implementação simplificada do parser HTTP
            headers = request.split('\r\n')
            method, path, _ = headers[0].split(' ')
            
            if method == 'GET' and path == '/question':
                question = self.questions[0]  # Simplificado
                content = json.dumps({
                    'question': question['question'],
                    'options': question['options']
                })
                response = self.create_http_response('200 OK', content, 'application/json')
            
            elif method == 'POST' and path == '/answer':
                content_length = 0
                for header in headers:
                    if 'Content-Length:' in header:
                        content_length = int(header.split(': ')[1])
                
                body = request.split('\r\n\r\n')[1][:content_length]
                answer_data = json.loads(body)
                
                # Lógica de verificação de resposta
                response = self.create_http_response('200 OK', '{"status": "received"}', 'application/json')
            
            else:
                response = self.create_http_response('404 Not Found', 'Not Found')
            
            ssl_socket.sendall(response.encode())

        except Exception as e:
            print(f"Error handling request: {e}")
            error_response = self.create_http_response('500 Internal Server Error', 'Server Error')
            ssl_socket.sendall(error_response.encode())
        finally:
            ssl_socket.close()

    def start(self):
        print(f"HTTPS Server running on {self.host}:{self.port}")
        try:
            while True:
                client_socket, addr = self.tcp_socket.accept()
                ssl_socket = self.context.wrap_socket(client_socket, server_side=True)
                Thread(target=self.handle_request, args=(ssl_socket,)).start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.tcp_socket.close()

if __name__ == "__main__":
    server = HTTPSServer()
    server.start()