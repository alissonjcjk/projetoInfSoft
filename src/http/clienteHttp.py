import socket
import json

class HTTPQuizClient:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.current_question = 0

    def send_request(self, method, path, body=None):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                
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
                
                response = s.recv(4096).decode()
                headers, body = response.split('\r\n\r\n', 1)
                return json.loads(body)
        
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def play(self):
        try:
            while True:
                # Pega a próxima pergunta
                question_data = self.send_request('GET', '/question')
                
                if not question_data or 'status' not in question_data:
                    print("Erro na comunicação com o servidor")
                    break
                    
                if question_data['status'] == 'completed':
                    print(f"\n🎉 Quiz concluído! Pontuação final: {question_data.get('final_score', 0)}")
                    break
                    
                if question_data['status'] != 'success':
                    print(f"\nErro: {question_data.get('message', 'Status desconhecido')}")
                    break
                
                # Mostra pergunta
                print(f"\n📝 Pergunta {question_data['question_number']}/{question_data['total_questions']}:")
                print(question_data['question'])
                for option in question_data['options']:
                    print(f"  {option}")
                
                # Destaque para última pergunta
                if question_data.get('is_last'):
                    print("\n⚠️ Esta é a última pergunta!")
                
                # Validação da resposta
                while True:
                    answer = input("\nSua resposta (A/B/C/D): ").strip().upper()
                    if answer in ['A', 'B', 'C', 'D']:
                        break
                    print("Resposta inválida! Digite apenas A, B, C ou D")
                
                # Envia resposta
                result = self.send_request('POST', '/answer', {'answer': answer})
                
                if not result or 'status' not in result:
                    print("Erro ao receber resultado do servidor")
                    break
                    
                # Feedback da resposta
                if result['correct']:
                    print("\n✅ Resposta correta!")
                else:
                    print(f"\n❌ Resposta incorreta! A correta era {result['correct_answer']}")
                
                print(f"📊 Pontuação atual: {result['score']}")
                
                # Encerra se for a última pergunta
                if result.get('quiz_completed'):
                    print(f"\n🎉 Quiz concluído! Pontuação final: {result['score']}")
                    break
                    
        except KeyboardInterrupt:
            print("\n⏹ Quiz interrompido pelo usuário")
        except Exception as e:
            print(f"\n⚠️ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    client = HTTPQuizClient()
    client.play()