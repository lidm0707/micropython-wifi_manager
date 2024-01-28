### """ is above tag


head = """
        <!DOCTYPE html>
            <html lang="en">
                <head>
                    <title>WiFi Manager</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="icon" href="data:,">
                </head>
"""

root = """
                <body>
                    <h1>WiFi Manager</h1>
                    <form action="/configure" method="post" accept-charset="utf-8">
                        <select name="ssid" class ="button" >{0}</select>
                        <p><label for="password">Password:&nbsp;</label><input class ="button" type="password" name="password"></p>
                        <p><label for="password">MQTT_IP:&nbsp;</label><input class ="button" type="text" name="ip"></p>
                        <p><label for="password">USER_TOPIC;</label><input class ="button" type="text" name="username"></p>
                        <p><label for="password">Pass_TOPIC:&nbsp;</label><input class ="button" type="password" name="password"></p>
                        <p><input type="submit" value="Connect" class ="button" ></p>
                    </form>
                </body>
            </html>
                    
"""

selectSSID = """
                <option value="{0}" id="{0}">{0}</option>
"""