import socket
import json

class HTTPQuizClient:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port

    def send_request(self, method, path, body=None):
        try:
            # Cria conexão TCP pura
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                
                # Constrói requisição HTTP manualmente
                request = f"{method} {path} HTTP/1.1\r\n"
                request += f"Host: {self.host}\r\n"
                
                if body:
                    body_str = json.dumps(body)
                    request += "Content-Type: application/json\r\n"
                    request += f"Content-Length: {len(body_str)}\r\n"
                    request += "\r\n"
                    request += body_str
                else:
                    request += "\r\n"
                
                s.sendall(request.encode())
                
                # Recebe resposta
                response = s.recv(4096).decode()
                headers, body = response.split('\r\n\r\n', 1)
                
                return json.loads(body)
        
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def play(self):
        # Exemplo de interação
        question = self.send_request('GET', '/question')
        print(question['question'])
        for option in question['options']:
            print(option)
        
        answer = input("Your answer: ")
        result = self.send_request('POST', '/answer', {'answer': answer})
        print(result)

if __name__ == "__main__":
    client = HTTPQuizClient()
    client.play()