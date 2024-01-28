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
stateWifi = not wm.isConnected()
stageMqtt = not mqt.isConnected()
wm.openAP(True)


# ? I want change to object SeviceManger

def pageConfig(url):
    wifi = 'ssid=([^&]*)&password=(.*)'
    mqttTOPIC = '&ip=(.*)&topicMQTT=(.*)'
    mqttUSER = '&userMQTT=(.*)&passMQTT=(.*)'
    regx = wifi+mqttTOPIC+mqttUSER
    match = re.search(regx, web.urlDecode(url))
    if match:
        ssid = match.group(1).decode('utf-8')
        password = match.group(2).decode('utf-8')
        ipQT = match.group(3).decode('utf-8')
        topicQT = match.group(4).decode('utf-8')
        userQT = match.group(5).decode('utf-8')
        passQT = match.group(6).decode('utf-8')
        print(ssid + password + ipQT + topicQT + userQT + passQT)
        pass
        
        if len(ssid) == 0:
            web.sendResponse("""
                <p>SSID must be providaded!</p>
                <p>Go back and try again!</p>
            """, 400)
        elif not wm.isConnected():
            wm.connect()
            if(not wm.isConnected()):
                if(not wm.wifiConnect(ssid ,password)):
                    web.sendResponse("""
                        <p>Could not connect to</p>
                        <h1>{0}</h1>
                        <p>Go back and try again!</p>
                    """.format(ssid))
                    time.sleep(5)
                else:
                    wm.writeConfigWifi(id = ssid , password = password)
                    mqt.writeConfig(id = userQT ,password = passQT,server = ipQT ,topic = topicQT)
                    web.sendResponse("""
                        <p>Successfully connected to</p>
                        <h1>{0}</h1>
                        <p>IP address: {1}</p>
                    """.format(ssid, wm.getAddress()[0]))
                    time.sleep(5)
                    wm.openAP(False)
                    machine.reset()
    else:
        web.sendResponse("""
            <p>Parameters not found!</p>
        """, 400)
        time.sleep(5)
    
def pageRoot():
    print('root')
    listSsid = []
    dropdownHtml = """ """
    for ssid, *_ in wm.scan():
        ssid = ssid.decode("utf-8")
        listSsid.append(ssid)
    for ssid in listSsid:
        dropdownHtml += selectSSID.format(ssid)
    web.sendResponse(root.format(dropdownHtml))

while stateWifi and stageMqtt:
    stateWifi = not wm.isConnected()
    stageMqtt = not mqt.isConnected()
    ## update state
    if(stateWifi):
        wm.connect()     
    if(stageMqtt):
        mqt.connect()
    #retry for conect   

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
    time.sleep(5)
    
        



