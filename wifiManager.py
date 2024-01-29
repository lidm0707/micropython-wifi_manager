# Author: Igor Ferreira
# License: MIT
# Version: 2.1.0
# Description: WiFi Manager for ESP8266 and ESP32 using MicroPython.

import network
import socket
import re
import ujson
#from binascii import a2b_base64, b2a_base64, hexlify, unhexlify
import time

class WifiManager:

    def __init__(self, ssid = 'esp32-ap', password = '12345678', reboot = True, debug = False):
        self.wlanSta = network.WLAN(network.STA_IF)
        self.wlanSta.active(True)
        self.wlanAp = network.WLAN(network.AP_IF)
        
        # Avoids simple mistakes with wifi ssid and password lengths, but doesn't check for forbidden or unsupported characters.
        if len(ssid) > 32:
            raise Exception('The SSID cannot be longer than 32 characters.')
        else:
            self.apSSID = ssid
        if len(password) < 8:
            raise Exception('The password cannot be less than 8 characters long.')
        else:
            self.apPASSWORD = password
            
        # Set the access point authentication mode to WPA2-PSK.
        self.apAUTHMODE = 3
        
        # The file were the credentials will be stored.
        # There is no encryption, it's just a plain text archive. Be aware of this security problem!
        self.config = 'config.json'
        # Prevents the device from automatically trying to connect to the last saved network without first going through the steps defined in the code.
        self.wlanSta.disconnect()
        self.wlanSta.scan()
        
        # Change to True if you want the device to reboot after configuration.
        # Useful if you're having problems with web server applications after WiFi configuration.
        self.reboot = reboot
        self.debug = debug

    def openAP(self,state:True|False):
        self.wlanAp.active(state)
        if state:
            self.wlanAp.config(essid = self.apSSID, password = self.apPASSWORD, authmode = self.apAUTHMODE)

    def scan(self):
        return self.wlanSta.scan()

    def connect(self):
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

    def writeConfigWifi(self,id = None ,password = None):
            key = 'wifi'
            #bytesPassword = password.encode()
            #password64 = b2a_base64(unhexlify(bytesPassword)).decode()
            try:
                with open('config.json') as file:
                    data = ujson.load(file)
                    # Check if key is in file
                    if key in data:
                        # Delete Key
                        del data[key]
                        cacheDict = dict(data)
                        # Update Cached Dict
                        cacheDict.update({key:{'id':id , 'password':password}})
                        with open('config.json','w') as file:
                            # Dump cached dict to json file
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
                        #password = hexlify(a2b_base64(data[key]['password'].encode())) 
                        profiles = {}
                        profiles[key] = {}
                        profiles[key]['id'] = data[key]['id']
                        profiles[key]['password'] = data[key]['password']
            return profiles
        except Exception as error:
            if self.debug:
                print(error)
            pass

        
    def wifiConnect(self, ssid, password):
        print('Trying to connect to:', ssid)
        if(ssid != ''):
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

    
    

