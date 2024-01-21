import time
from umqtt.simple import MQTTClient
from binascii import a2b_base64, b2a_base64, hexlify, unhexlify



class MqttManager:
    def __init__(self, name ='mqttClient' ,sever = '192.168.1.101',userMqtt = 'admin' ,passwordMqtt = None,debug = False):
        self.name = name
        self.sever = sever
        self.userMqtt = userMqtt
        self.passwordMqtt = passwordMqtt
        self.MQTTClient = MQTTClient
        self.stage = False
        self.debug = debug
    
    def isConnected(self):
        return self.stage
        
    def writeConfig(self,id = None ,password = None):
            key = 'mqtt'
            bytesPassword = password.encode()
            password64 = b2a_base64(unhexlify(bytesPassword)).decode()
            try:
                with open('config.json') as file:
                    data = ujson.load(file)
                    # Check if key is in file
                    if key in data:
                        # Delete Key
                        del data[key]
                        cacheDict = dict(data)
                        # Update Cached Dict
                        cacheDict.update({key:{'id':id , 'password':password64}})
                        with open('config.json','w') as file:
                            # Dump cached dict to json file
                            ujson.dump(cacheDict, file)
                            self.isconnected
                            print('saved')            
            except Exception as error:
                if self.debug:
                    self.isconnected = False
                    print(error)
                pass

    def readConfig(self):
        key = 'mqtt'
        print('use read Config')
        try:
            profiles = {}
            with open(self.config) as file:
                data = ujson.load(file)
                if key in data:
                    if profiles[key]['id'] is not None:
                        password = hexlify(a2b_base64(data[key]['password'].encode()))
                        profiles[key]['id'] = password
            return profiles
        except Exception as error:
            if self.debug:
                print(error)
            pass        
    
    def connect(self):
        profiles = self.readConfig()
        network = 'mqtt'
        try:     
            if profiles[network]['id'] is not None:
                mClient = self.MQTTClient(self.name, self.server,self.port, user = profiles[network]['id'] ,password = profiles[network]['password'])
                mClient.connect()
                self.isConnected = True
                return
                
        except:
            print('can\'t connected')
            print('Could not connect to any MQTT')
            
        
    
