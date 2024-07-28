from wifiManager import WifiManager
from mqttManager import MqttManager
from webServer import WebServer
from html import rootHTML, selectSSID
import time
import machine
import _thread

# Example of usage
_thread.stack_size(32 * 1024)
wm = WifiManager()
mqt = MqttManager(debug=True)
web = WebServer(debug=True)

@web.route('/')
def root(request):
    print('root')
    print(request)
    listSsid = []
    dropdownHtml = ''' '''
    for ssid, *_ in wm.scan():
        ssid = ssid.decode('utf-8')
        listSsid.append(ssid)
    for ssid in listSsid:
        dropdownHtml += selectSSID.format(ssid)
    web.sendResponse(rootHTML.format(dropdownHtml))
        
@web.route('/configure')
def configure(request):
    print(request)
    print('pageConfig')
    wifi = 'ssid=([^&]*)&pwd=([^&]*)'
    mqtt = '&ip=([^&]*)&username=([^&]*)&pwdm=([^&]*)'
    regx = wifi + mqtt
    match = web.requestX(regx)
    print(match)
    if not match:
        web.sendResponse('''
            <p>Parameters not found!</p>
        ''', 400)
    elif match:
        ssid = match.group(1).decode('utf-8')
        password = match.group(2).decode('utf-8')
        ipQT = match.group(3).decode('utf-8')
        userQT = match.group(4).decode('utf-8')
        passQT = match.group(5).decode('utf-8')
        print(ssid, password, ipQT, userQT)
        if len(ssid) == 0:
            web.sendResponse('''
                <p>SSID must be provided!</p>
                <p>Go back and try again!</p>
            ''', 400)
        else:
            wm.wifiConnect(ssid, password)
            time.sleep(5)  # Wait for Wi-Fi connection to complete
            if wm.isConnected():
                wm.writeConfigWifi(id=ssid, password=password)
                mqt.writeConfig(id=userQT, password=passQT, server=ipQT)
                web.sendResponse(f'''
                    <p>Successfully connected to</p>
                    <h1>{ssid}</h1>
                    <p>IP address: {wm.getAddress()[0]}</p>
                ''')
                time.sleep(5)
                machine.reset()
            else:
                web.sendResponse(f'''
                    <p>Could not connect to</p>
                    <h1>{ssid}</h1>
                    <p>Go back and try again!</p>
                ''')

def sendMqt():
    i = 0
    print('stard MQTT')
    while True:     
        time.sleep(5)
        i += 1
        try:
            mqt.connect()
            if mqt.isConnected():
                mqt.publish('hello/topic', f'hello{str(i)} ip:{wm.getAddress()}')
                mqt.disconnect()
                print(f'hello{str(i)}')
                time.sleep(1)
        except Exception as error: 
            print(f'MQTT ERROR {error}')

def main():
    wm.openAP(True)
    wm.connect()
    _thread.start_new_thread(sendMqt, ())
    _thread.start_new_thread(web.run, ())
    

main()

