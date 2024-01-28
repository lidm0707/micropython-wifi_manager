import network
import socket
import re
from html import head
from css import css
import time

#192.168.4.1
class webServer:
    def __init__(self,debug=False):
        
        self.debug = debug
        self.server_socket = socket.socket()
        self.server_socket.close()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', 80))
        self.server_socket.listen(1)
        
        
        
    def run(self):
        print("start web")
        self.client, addr = self.server_socket.accept()
        self.request = b''
        try:
            self.client.settimeout(5.0)
            try:
                while True:
                    if '\r\n\r\n' in self.request:
                        # Fix for Safari browser
                        self.request += self.client.recv(1024)
                        break
                    self.request += self.client.recv(256)
                    print(self.request)
                    print("request")
                    time.sleep(1)
            except Exception as error:
                # It's normal to receive timeout errors in this stage, we can safely ignore them.
                if self.debug:
                    print(error)
                pass

        except Exception as error:
            if self.debug:
                print(error)
            return

            
    def urlDecode(self, urlString):

        # Source: https://forum.micropython.org/viewtopic.php?t=3076
        # unquote('abc%20def') -> b'abc def'
        # Note: strings are encoded as UTF-8. This is only an issue if it contains
        # unescaped non-ASCII characters, which URIs should not.

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
            
    def rout(self):
        if self.request and self.request != None:
            if self.debug:
                print(self.urlDecode(self.request))
            url = re.search('(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP', self.request).group(1).decode('utf-8').rstrip('/')
            print(url)
            print("self.request rout")
            print(self.request)
            print("rout")
            return url , self.request
        

    def sendHeader(self, status_code = 200):
        self.client.send("""HTTP/1.1 {0} OK\r\n""".format(status_code))
        self.client.send("""Content-Type: text/html\r\n""")
        self.client.send("""Connection: close\r\n""")


    def sendResponse(self, payload, status_code = 200):
        self.sendHeader(status_code)
        body = """<body>{0}</body></html>""".format(payload)
        self.client.sendall(head + css + body)
        self.client.close()


    



