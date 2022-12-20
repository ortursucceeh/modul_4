import mimetypes
import pathlib
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote_plus
import socket
from datetime import datetime
import json


HOST = '127.0.0.1'
SERVER_PORT = 3000
CLIENT_PORT = 5000

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def send_html_file(self, filename: str, status: int = 200):
        self.send_response(status,)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def do_GET(self):
        url = self.path

        match url:
            case '/':
                self.send_html_file('index.html')
            case '/message':
                self.send_html_file('message.html') 
            case _:
                if pathlib.Path().joinpath(url[1:]).exists():
                     self.send_static()
                else:
                    self.send_html_file('error.html', 404)
        

    def do_POST(self): 
        data: bytes = self.rfile.readline(int(self.headers['Content-Length']))
        self.send_response(302)
        self.send_data(data=data)
        self.send_header('Location', '/message')
        self.end_headers()

    def send_data(self, data: bytes):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('127.0.0.1', CLIENT_PORT))
        sock.send(data)

    def send_static(self):
        self.send_response(200) 
        mt = mimetypes.guess_type(url=self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

def run_web_server():
    httpd = HTTPServer((HOST, SERVER_PORT), SimpleHTTPRequestHandler)
    try:
        httpd.serve_forever()
        print('Running web server...')
    except KeyboardInterrupt:
        httpd.server_close()
            

def run_socket_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, CLIENT_PORT))
    try:
        while True:
            data, address = server.recvfrom(1024)
            print(f'Received data: {data.decode()} from: {address}')
            write_in_json(data)

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        server.close()
    
def write_in_json(data: bytes):
    query_data: str = unquote_plus(data.decode())
    data: dict = {key: value for key, value in [el.split('=') for el in query_data.split('&')]}
    new_data: dict = {str(datetime.now()): data}
    
    json_data: dict = json.load(open('storage\data.json'))
    json_data.update(new_data)

    with open('storage\data.json', 'w') as file:
        json.dump(json_data, file, indent=4)
        print(f'Record was added to json.file\n')




if __name__ == '__main__':
    web_server = Thread(target=run_web_server)
    socket_server = Thread(target=run_socket_server)

    web_server.start()
    socket_server.start()

    web_server.join()
    socket_server.join()

    