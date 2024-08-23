from wifiManager import WifiManager
from mqttManager import MqttManager
from webServer import WebServer
from html import rootHTML, selectSSID
import time
import machine
import _thread

_thread.stack_size(32 * 1024)

wm = WifiManager(debug=True)
mqt = MqttManager(debug=True)
web = WebServer(debug=True)


def parseQs(qs):
    params = {}
    pairs = qs.split('&')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            params[key] = value
    return params

@web.route('/')
def root(request):
    print('Received request at root:', request)
    ssidList = [ssid.decode('utf-8') for ssid, *_ in wm.scan()]
    dropdownHtml = ''.join(selectSSID.format(ssid) for ssid in ssidList)
    responseHtml = rootHTML.format(dropdownHtml)
    web.sendResponse(responseHtml)
            
@web.route('/configure')
def configure(request):
    print('Received request at /configure:', request)
    
    try:
        headers, body = request.split(b'\r\n\r\n', 1)
    except ValueError:
        web.sendResponse('<p>Invalid request format!</p><p>Please try again.</p>', 400)
        return
    
    params = parseQs(body.decode('utf-8'))
    print(params)

    ssid = params.get('ssid', '')
    password = params.get('pwd', '')
    ipQt = params.get('ip', '')
    userQt = params.get('username', '')
    passQt = params.get('pwdm', '')

    if not ssid:
        web.sendResponse('<p>SSID must be provided!</p><p>Please try again.</p>', 400)
        return
    
    web.sendResponse('<p>Connecting to Wi-Fi...</p>')
    wm.wifiConnect(ssid, password)
    time.sleep(5) 
    
    if wm.isConnected():
        wm.writeConfigWifi(id=ssid, password=password)
        mqt.writeConfig(id=userQt, password=passQt, server=ipQt)
        ipAddress = wm.getAddress()[0]
        successHtml = f'''
            <p>Successfully connected to <strong>{ssid}</strong></p>
            <p>IP address: {ipAddress}</p>
            <p>MQTT configuration saved successfully.</p>
        '''
        web.sendResponse(successHtml)
        time.sleep(2)
    else:
        errorHtml = f'''
            <p>Could not connect to <strong>{ssid}</strong></p>
            <p>Please check your credentials and try again.</p>
        '''
        web.sendResponse(errorHtml, 400)

def sendMqtt():
    print('Starting MQTT thread')
    counter = 0
    while True:     
        time.sleep(5)
        counter += 1
        try:
            mqt.connect()
            if mqt.isConnected():
                message = f'hello {counter} ip: {wm.getAddress()}'
                mqt.publish('hello/topic', message)
                mqt.disconnect()
                print('Published message:', message)
        except Exception as error: 
            print('MQTT ERROR:', error)

def main():
    wm.openAP(True)
    wm.connect()
    _thread.start_new_thread(sendMqtt, ())
    _thread.start_new_thread(web.run, ())

if __name__ == '__main__':
    main()


