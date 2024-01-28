import time
from umqtt.simple import MQTTClient
from binascii import a2b_base64, b2a_base64, hexlify, unhexlify
import ujson



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
        
    def writeConfig(self,id,password,server,topic):
            print('write mqtt')
            key = 'mqtt'
            try:
                with open('config.json') as file:
                    data = ujson.load(file)
                    # Check if key is in file
                    if key in data:
                        # Delete Key
                        del data[key]
                        cacheDict = dict(data)
                        # Update Cached Dict
                        cacheDict.update({key:{'id':id , 'password':password,'server':server,'topic':topic}})
                        with open('config.json','w') as file:
                            # Dump cached dict to json file
                            ujson.dump(cacheDict, file)
                            print('mqtt is saved')            
            except Exception as error:
                if self.debug:
                    print(error)
                pass

    def readConfig(self):
        key = 'mqtt'
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
                        profiles[key]['sever'] = data[key]['sever']
                        profiles[key]['topic'] = data[key]['topic']
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
            
        
    

