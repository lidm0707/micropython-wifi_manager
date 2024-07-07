import socket
from html import head
from css import css
import re
import time

#192.168.4.1
class WebServer:
    def __init__(self, debug=False):
        self.debug = debug
        self.server_socket = socket.socket()
        self.server_socket.close()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', 80))
        self.server_socket.listen(1)
        self.routes = {}

    def __addRoute(self, path, handler):
        self.routes[path] = handler

    def route(self, path):
        def decorator(func):
            self.__addRoute(path, func)
            return func  # Return the function without calling it
        return decorator

    def run(self):
        print("Starting web server...")
        while True:
            self.client, addr = self.server_socket.accept()
            self.request = b''
            try:
                self.client.settimeout(5.0)
                while True:
                    if b'\r\n\r\n' in self.request:
                        break
                    self.request += self.client.recv(256)
                    time.sleep(3)
            except Exception as error:
                if self.debug:
                    print(error)

            if self.request:
                url = re.search('(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP', self.request).group(1).decode('utf-8').rstrip('/')
                if(not url):
                    url = '/'
                print("stard routes")
                # print(self.request)
                print(self.routes)
                print(url)
                if url in self.routes:
                    self.routes[url]()
                else:
                    self.sendResponse("404 Not Found", 404)

    def urlDecode(self, urlString):
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
        


    



