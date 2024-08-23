import network
import socket
import re
import ujson
import time
##192.168.4.1
class WifiManager:
    def __init__(self, ssid='esp32-ap', password='12345678', reboot=True, debug=False):
        self.wlanSta = network.WLAN(network.STA_IF)
        self.wlanSta.active(True)
        self.wlanAp = network.WLAN(network.AP_IF)
        
        if len(ssid) > 32:
            raise Exception('The SSID cannot be longer than 32 characters.')
        else:
            self.apSSID = ssid
        if len(password) < 8:
            raise Exception('The password cannot be less than 8 characters long.')
        else:
            self.apPASSWORD = password
            
        self.apAUTHMODE = 3
        self.config = 'config.json'
        self.wlanSta.disconnect()
        self.wlanSta.scan()

        self.reboot = reboot
        self.debug = debug

    def openAP(self, state: bool):
        self.wlanAp.active(state)
        if state:
            self.wlanAp.config(essid=self.apSSID, password=self.apPASSWORD, authmode=self.apAUTHMODE)

    def scan(self):
        return self.wlanSta.scan()

    def isConnected(self):
        if self.wlanSta.isconnected():
            return
        profiles = self.readConfigWifi()
        print("profiles")
        print(profiles)     
        for ssid, *_ in self.wlanSta.scan():
            ssid = ssid.decode("utf-8")
            print(ssid)
            if profiles is not None:
                if profiles['wifi']['id'] is not None:
                    if ssid in profiles['wifi']['id']:
                        password = profiles['wifi']['password']
                        if self.wifiConnect(ssid, password):
                            return 
        print('Could not connect to any WiFi network. Starting the configuration portal...')

    def disConnect(self):
        if self.wlanSta.isconnected():
            self.wlanSta.disconnect()

    def isConnected(self):
        return self.wlanSta.isconnected()

    def getAddress(self):
        return self.wlanSta.ifconfig()

    def writeConfigWifi(self, id=None, password=None):
        key = 'wifi'
        try:
            with open(self.config) as file:
                data = ujson.load(file)
                if key in data:
                    del data[key]
                cacheDict = dict(data)
                cacheDict.update({key: {'id': id, 'password': password}})
                with open(self.config, 'w') as file:
                    ujson.dump(cacheDict, file)
                    print('wifi is saved')
        except Exception as error:
            if self.debug:
                print(error)
            pass

    def readConfigWifi(self):
        key = 'wifi'
        print('use read Config')
        try:
            with open(self.config) as file:
                data = ujson.load(file)
                if key in data:
                    print(key)
                    if data[key]['id'] is not None:
                        profiles = {}
                        profiles[key] = {}
                        profiles[key]['id'] = data[key]['id']
                        profiles[key]['password'] = data[key]['password']
                        return profiles
        except Exception as error:
            if self.debug:
                print(error)
            pass
        return None

    def wifiConnect(self, ssid, password):
        print('Trying to connect to:', ssid)
        if ssid:
            self.wlanSta.connect(ssid, password)
            for _ in range(100):
                if self.wlanSta.isconnected():
                    print('\nConnected! Network information:', self.wlanSta.ifconfig())
                    return True
                else:
                    print('.', end='')
                    time.sleep(1)
            print('\nConnection failed!')
            self.wlanSta.disconnect()
            return False
