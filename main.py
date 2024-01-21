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
mqt = MqttManager()
web = webServer()
routRoot = ''
routConfig = 'config'
stateWifi = not(wm.isConnected())
stageMqtt = not(mqt.isConnected())


def pageConfig(url):
    match = re.search('ssid=([^&]*)&password=(.*)', wm.urlDecode(url))
    if match:
        ssid = match.group(1).decode('utf-8')
        password = match.group(2).decode('utf-8')
        
        if len(ssid) == 0:
            web.sendResponse("""
                <p>SSID must be providaded!</p>
                <p>Go back and try again!</p>
            """, 400)
        elif not wm.isConnected():
            wm.connect()
            if(not wm.isConnected()):
                wm.wifiConnect(id = ssid , password = password)
                if(not wm.isConnected()):
                    web.sendResponse("""
                        <p>Could not connect to</p>
                        <h1>{0}</h1>
                        <p>Go back and try again!</p>
                    """.format(ssid))
                    time.sleep(5)
                else:
                    wm.writeConfigWifi(id = ssid , password = password)
                    web.sendResponse("""
                        <p>Successfully connected to</p>
                        <h1>{0}</h1>
                        <p>IP address: {1}</p>
                    """.format(ssid, wm.wlanSta.scan()[0]))
                    time.sleep(5)
                    machine.reset()
    else:
        web.sendResponse("""
            <p>Parameters not found!</p>
        """, 400)
        time.sleep(5)
    
def pageRoot():
    listSsid = []
    dropdownHtml = """ """
    for ssid, *_ in wm.scan():
        ssid = ssid.decode("utf-8")
        listSsid.append(ssid)
    for ssid in listSsid:
        dropdownHtml += selectSSID.format(ssid)
    print(dropdownHtml)
    web.sendResponse(root.format(dropdownHtml))

while stateWifi and stageMqtt:
    stateWifi = not(wm.isConnected())
    stageMqtt = not(mqt.isConnected())
    ## update state
    if(stateWifi):
        wm.connect()     
    if(stageMqtt):
        mqt.connect()
    #retry for conect   
    wm.openAP(True)
    web.run()
    path = web.rout()
    
    if path == routRoot:
        pageRoot()
    elif path == routConfig:
        pageConfig(path)
    time.sleep(5)
    
        


