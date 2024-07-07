from wifiManager import WifiManager
from mqttManager import MqttManager
from webServer import WebServer
from html import rootHTML , selectSSID
import time
import machine
import _thread

# Example of usage

wm = WifiManager()
mqt = MqttManager(debug = True)
web = WebServer()

wm.openAP(True)   
    
@web.route('/')
def root():
    print('root')
    
    wm.connect()
    
    if(not wm.isConnected()):
        listSsid = []
        dropdownHtml = ''' '''
        for ssid, *_ in wm.scan():
            ssid = ssid.decode('utf-8')
            listSsid.append(ssid)
        for ssid in listSsid:
            dropdownHtml += selectSSID.format(ssid)
        web.sendResponse(rootHTML.format(dropdownHtml))
        

@web.route('/configure')
def configure():
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
        if len(ssid) == 0:
            web.sendResponse('''
                <p>SSID must be providaded!</p>
                <p>Go back and try again!</p>
            ''', 400)
        elif not wm.isConnected:
            wm.wifiConnect(ssid ,password)
            if not wm.isConnected:
                wm.writeConfigWifi(id = ssid , password = password)
                mqt.writeConfig(id = userQT ,password = passQT,server = ipQT)
                web.sendResponse('''
                    <p>Successfully connected to</p>
                    <h1>{0}</h1>
                    <p>IP address: {1}</p>
                '''.format(ssid, wm.getAddress()[0]))
                time.sleep(5)
                machine.reset()
            else:
                web.sendResponse('''
                    <p>Could not connect to</p>
                    <h1>{0}</h1>
                    <p>Go back and try again!</p>
                '''.format(ssid))
                time.sleep(5)

def sendMqt():
    try:
        if(mqt.isConnected):
            for i in range(10):
                mqt.connect()
                mqt.publish('hello/topic', 'hello'+str(i))
                mqt.disconect()
                print('hello'+str(i))
                time.sleep(1)
                
            mqt.publish('hello/topic', 'disconect')
    except OSError: 
        print('OSError')



_thread.start_new_thread(web.run, ())
_thread.start_new_thread(sendMqt, ())











