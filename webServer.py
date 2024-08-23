import socket
import re
import time
from html import head
from css import css

class WebServer:
    def __init__(self, debug=False):
        self.debug = debug
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', 80))
        self.server_socket.listen(4)
        self.routes = {}

    def __addRoute(self, path, handler):
        self.routes[path] = handler

    def route(self, path):
        def decorator(func):
            self.__addRoute(path, func)
            return func
        return decorator

    def run(self):
        print("Starting web server...")
        while True:
            try:
                self.client, addr = self.server_socket.accept()
                self.request = b''
                while True:
                    if b'\r\n\r\n' in self.request:
                        break
                    data = self.client.recv(256)
                    if not data:
                        break
                    self.request += data
                check = self.__requestX(r'(?:GET|POST) (\/.*?) HTTP\/')
                if check:
                    url = check.group(1).decode('utf-8').rstrip()
                else:
                    url = check
                if url:
                    if url in self.routes:
                        self.routes[url](self.urlDecode())
                    else:
                        self.sendResponse("404 Not Found", 404)
                self.client.close()
            except Exception as error:
                if self.debug:
                    print(f"Exception in run loop: {error}")
                if self.client:
                    self.client.close()

    def urlDecode(self):
        urlString = self.request
        if not urlString:
            return b''

        if isinstance(urlString, str):
            urlString = urlString.encode('utf-8')

        bits = urlString.split(b'%')

        if len(bits) == 1:
            return urlString

        res = [bits[0]]
        appnd = res.append
        hextobyte_cache = {}

        for item in bits[1:]:
            try:
                code = item[:2]
                char = hextobyte_cache.get(code)
                if char is None:
                    char = hextobyte_cache[code] = bytes([int(code, 16)])
                appnd(char)
                appnd(item[2:])
            except Exception as error:
                if self.debug:
                    print(error)
                appnd(b'%')
                appnd(item)
        return b''.join(res)

    def sendHeader(self, status_code=200):
        self.client.send(b"HTTP/1.1 {0} OK\r\n".format(status_code))
        self.client.send(b"Content-Type: text/html\r\n")
        self.client.send(b"Connection: close\r\n\r\n")

    def sendResponse(self, payload, status_code=200):
        self.sendHeader(status_code)
        body = "<body>{0}</body></html>".format(payload)
        self.client.sendall(head + css + body)
        self.client.close()

    def __requestX(self, reg):
        pattern = re.compile(reg)
        res = pattern.search(self.urlDecode())
        return res

