# Author: Igor Ferreira
# License: MIT
# Version: 2.1.0
# Description: WiFi Manager for ESP8266 and ESP32 using MicroPython.

import machine
import network
import socket
import re
import time
from ucryptolib import aes
from html import head
from css import css
from umqtt.simple import MQTTClient


class WifiManager:

    def __init__(self, ssid = 'WifiManager', password = 'wifimanager', reboot = True, debug = False):
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_sta.active(True)
        self.wlan_ap = network.WLAN(network.AP_IF)
        self.MQTTClient = MQTTClient
        
        # Avoids simple mistakes with wifi ssid and password lengths, but doesn't check for forbidden or unsupported characters.
        if len(ssid) > 32:
            raise Exception('The SSID cannot be longer than 32 characters.')
        else:
            self.ap_ssid = ssid
        if len(password) < 8:
            raise Exception('The password cannot be less than 8 characters long.')
        else:
            self.ap_password = password
            
        # Set the access point authentication mode to WPA2-PSK.
        self.ap_authmode = 3
        
        # The file were the credentials will be stored.
        # There is no encryption, it's just a plain text archive. Be aware of this security problem!
        self.wifi_credentials = 'wifi.dat'
        self.private_key = 'key.dat'
        # Prevents the device from automatically trying to connect to the last saved network without first going through the steps defined in the code.
        self.wlan_sta.disconnect()
        
        # Change to True if you want the device to reboot after configuration.
        # Useful if you're having problems with web server applications after WiFi configuration.
        self.reboot = reboot
        self.debug = debug
        
    def read_keys(self):
        lines = []
        try:
            with open(self.private_key) as file:
                lines = file.readlines()
        except Exception as error:
            if self.debug:
                print(error)
            pass
        p_key = None
        for line in lines:
            name, key = line.strip().split(';')
            p_key = key
        return eval(p_key)
    
        # Function to encrypt a string using AES
    def encrypt_string(self, input_string ):
        key = self.read_keys()
        cipher = aes(key, 1)
        input_string = input_string.encode('utf-8')
        # Ensure the input string length is a multiple of 16 (AES block size)
        padded_input = input_string + b'\x00' * (16 - len(input_string) % 16)
        encrypted = cipher.encrypt(padded_input)
        return encrypted
    
    # Function to decrypt an AES-encrypted string
    def decrypt_string(self, encrypted_string ):
        cipher = aes(self.read_keys(), 1)
        encrypted_string = eval(encrypted_string)
        decrypted = cipher.decrypt(encrypted_string)
        return decrypted.rstrip(b'\x00')  # Remove padding
     

    def connect(self):
        if self.wlan_sta.isconnected():
            return
        profiles = self.read_credentials()
        for ssid, *_ in self.wlan_sta.scan():
            ssid = ssid.decode("utf-8")
            if ssid in profiles:
                password = profiles[ssid]
                if self.wifi_connect(ssid, password):
                    return
        print('Could not connect to any WiFi network. Starting the configuration portal...')
        self.web_server()
        
    
    def disconnect(self):
        if self.wlan_sta.isconnected():
            self.wlan_sta.disconnect()


    def is_connected(self):
        return self.wlan_sta.isconnected()


    def get_address(self):
        return self.wlan_sta.ifconfig()


    def write_credentials(self, profiles):
        print('use write_credentials')
        
        lines = []
        for ssid, password in profiles.items():
            print(ssid)
            print(password)
            en_password = self.encrypt_string(password)
            print(en_password)
            lines.append('{0};{1}\n'.format(ssid, en_password))
        with open(self.wifi_credentials, 'w') as file:
            file.write(''.join(lines))
        file =   open(self.wifi_credentials, 'w')  
        print(file)
        



    def read_credentials(self):
        print('use read credentials')
        lines = []
        try:
            with open(self.wifi_credentials) as file:
                lines = file.readlines()
        except Exception as error:
            if self.debug:
                print(error)
            pass
        profiles = {}
        for line in lines:
            ssid, password = line.strip().split(';')
            print(self.decrypt_string(password))
            profiles[ssid] = self.decrypt_string(password)
        return profiles
    

        

    def wifi_connect(self, ssid, password):
        print('Trying to connect to:', ssid)
        self.wlan_sta.connect(ssid, password)
        for _ in range(100):
            if self.wlan_sta.isconnected():
                print('\nConnected! Network information:', self.wlan_sta.ifconfig())
                return True
            else:
                print('.', end='')
                time.sleep_ms(100)
        print('\nConnection failed!')
        self.wlan_sta.disconnect()
        return False

    
    def web_server(self):
        self.wlan_ap.active(True)
        self.wlan_ap.config(essid = self.ap_ssid, password = self.ap_password, authmode = self.ap_authmode)
        server_socket = socket.socket()
        server_socket.close()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', 80))
        server_socket.listen(1)
        print('Connect to', self.ap_ssid, 'with the password', self.ap_password, 'and access the captive portal at', self.wlan_ap.ifconfig()[0])
        while True:
            if self.wlan_sta.isconnected():
                self.wlan_ap.active(False)
                if self.reboot:
                    print('The device will reboot in 5 seconds.')
                    time.sleep(5)
                    machine.reset()
            self.client, addr = server_socket.accept()
            try:
                self.client.settimeout(5.0)
                self.request = b''
                try:
                    while True:
                        if '\r\n\r\n' in self.request:
                            # Fix for Safari browser
                            self.request += self.client.recv(1024)
                            break
                        self.request += self.client.recv(256)
                except Exception as error:
                    # It's normal to receive timeout errors in this stage, we can safely ignore them.
                    if self.debug:
                        print(error)
                    pass
                if self.request:
                    if self.debug:
                        print(self.url_decode(self.request))
                    url = re.search('(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP', self.request).group(1).decode('utf-8').rstrip('/')
                    if url == '':
                        self.handle_root()
                    elif url == 'configure':
                        self.handle_configure()
                    else:
                        self.handle_not_found()
            except Exception as error:
                if self.debug:
                    print(error)
                return
            finally:
                self.client.close()


    def send_header(self, status_code = 200):
        self.client.send("""HTTP/1.1 {0} OK\r\n""".format(status_code))
        self.client.send("""Content-Type: text/html\r\n""")
        self.client.send("""Connection: close\r\n""")


    def send_response(self, payload, status_code = 200):
        self.send_header(status_code)
        body = """<body>{0}</body></html>""".format(payload)
        self.client.sendall(head + css + body)
        self.client.close()


    def handle_root(self):
        self.send_header()
        self.client.sendall(head + css + """
                <body>
                    <h1>WiFi Manager</h1>
                    <form action="/configure" method="post" accept-charset="utf-8">
        """)
        # .format(self.ap_ssid)
        listSsid = []
        for ssid, *_ in self.wlan_sta.scan():
            ssid = ssid.decode("utf-8")
            listSsid.append(ssid)

        # Now, generate the HTML with the dropdown list
        dropdown_html = """
            <select name="ssid" class ="button" >
        """
        
        for ssid in listSsid:
            dropdown_html += """
                <option value="{0}" id="{0}">{0}</option>
            """.format(ssid)
        dropdown_html += """
            </select>
        """

        # Send the HTML to the client
        self.client.sendall(dropdown_html)
        self.client.sendall("""
                        <p><label for="password">Password:&nbsp;</label><input class ="button" type="password" name="password"></p>
                        <p><input type="submit" value="Connect" class ="button" ></p>
                    </form>
                </body>
            </html>
        """)
        self.client.close()


    def handle_configure(self):
        print(self.url_decode(self.request))
        match = re.search('ssid=([^&]*)&password=(.*)&mqtt=(.*)&topic=(.*)&usermqtt=(.*)&passmqtt=(.*)', self.url_decode(self.request))
        if match:
            ssid = match.group(1).decode('utf-8')
            password = match.group(2).decode('utf-8')
            mqtt = match.group(3).decode('utf-8')
            topic = match.group(4).decode('utf-8')
            usermqtt = match.group(5).decode('utf-8')
            passmqtt = match.group(6).decode('utf-8')
            if len(ssid) == 0:
                self.send_response("""
                    <p>SSID must be providaded!</p>
                    <p>Go back and try again!</p>
                """, 400)
            elif self.wifi_connect(ssid, password):
                self.send_response("""
                    <p>Successfully connected to</p>
                    <h1>{0}</h1>
                    <p>IP address: {1}</p>
                """.format(ssid, self.wlan_sta.ifconfig()[0]))
                profiles = self.read_credentials()
                profiles[ssid] = password
                print(profiles[ssid])
                self.write_credentials(profiles)
                time.sleep(5)
            else:
                self.send_response("""
                    <p>Could not connect to</p>
                    <h1>{0}</h1>
                    <p>Go back and try again!</p>
                """.format(ssid))
                time.sleep(5)
        else:
            self.send_response("""
                <p>Parameters not found!</p>
            """, 400)
            time.sleep(5)


    def handle_not_found(self):
        self.send_response("""
            <p>Page not found!</p>
        """, 404)


    def url_decode(self, url_string):

        # Source: https://forum.micropython.org/viewtopic.php?t=3076
        # unquote('abc%20def') -> b'abc def'
        # Note: strings are encoded as UTF-8. This is only an issue if it contains
        # unescaped non-ASCII characters, which URIs should not.

        if not url_string:
            return b''

        if isinstance(url_string, str):
            url_string = url_string.encode('utf-8')

        bits = url_string.split(b'%')

        if len(bits) == 1:
            return url_string

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
