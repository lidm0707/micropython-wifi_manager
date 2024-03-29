from wifiManager import WifiManager
from mqttManager import MqttManager
from webServer import webServer
from html import root 
from html import selectSSID
import re
import time
import machine

# Example of usage

wm = WifiManager()
mqt = MqttManager(debug = True)
web = webServer()
routRoot = ''
routConfig = 'configure'
wm.connect()     
def callBack(callFn):
    return not callFn()


def pageRoot():
    print('root')
    listSsid = []
    dropdownHtml = ''' '''
    for ssid, *_ in wm.scan():
        ssid = ssid.decode('utf-8')
        listSsid.append(ssid)
    for ssid in listSsid:
        dropdownHtml += selectSSID.format(ssid)
    web.sendResponse(root.format(dropdownHtml))

def pageConfig(url):
    print('pageConfig')
    wifi = 'ssid=([^&]*)&password=(.*)'
    mqtt = '&ip=(.*)&username=(.*)&password=(.*)'
    regx = wifi+mqtt
    match = re.search(regx, web.urlDecode(url))
    if not match:
        web.sendResponse('''
            <p>Parameters not found!</p>
        ''', 400)
        time.sleep(5)
    elif match:
        ssid = match.group(1).decode('utf-8')
        password = match.group(2).decode('utf-8')
        ipQT = match.group(3).decode('utf-8')
        userQT = match.group(4).decode('utf-8')
        passQT = match.group(5).decode('utf-8')
        pass
        
        if len(ssid) == 0:
            web.sendResponse('''
                <p>SSID must be providaded!</p>
                <p>Go back and try again!</p>
            ''', 400)
        elif callBack(wm.isConnected) or callBack(mqt.isConnected):
            wm.wifiConnect(ssid ,password)
            if callBack(wm.isConnected):
                wm.writeConfigWifi(id = ssid , password = password)
                mqt.writeConfig(id = userQT ,password = passQT,server = ipQT)
                web.sendResponse("""
                    <p>Successfully connected to</p>
                    <h1>{0}</h1>
                    <p>IP address: {1}</p>
                """.format(ssid, wm.getAddress()[0]))
                time.sleep(5)
                machine.reset()
            elif callBack(mqt.isConnected):
                mqt.writeConfig(id = userQT ,password = passQT,server = ipQT)
                web.sendResponse("""
                    <p>Successfully connected to</p>
                    <h1>TRY connect MQTT</h1>
                    <p>IP address: {1}</p>
                """)
                time.sleep(5)
                machine.reset()
            else:
                web.sendResponse('''
                    <p>Could not connect to</p>
                    <h1>{0}</h1>
                    <p>Go back and try again!</p>
                '''.format(ssid))
                time.sleep(5)

    


wm.openAP(True)
while callBack(wm.isConnected) or callBack(mqt.isConnected):
    web.run()
    path = ''
    routOb = web.rout()
    if(routOb != None):
        path = routOb[0]
        url = routOb[1]
        if path == routRoot:
            pageRoot()
        elif path == routConfig:
            pageConfig(url)
            if callBack(wm.isConnected):
                 wm.connect()     
            if callBack(mqt.isConnected):
                  mqt.connect()
    print("loop")
    time.sleep(1)
    
print('wifi connect')
wm.openAP(False)


try:
    if(not callBack(mqt.isConnected)):
        for i in range(10):
            mqt.publish('hello/topic', 'hello'+str(i))
            print('hello'+str(i))
            time.sleep(1)
            
        mqt.publish('hello/topic', 'disconect')
except OSError: 
    print('OSError')






