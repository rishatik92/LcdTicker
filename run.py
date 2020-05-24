from QueueDispetcher import get_settings, SETTINGS_FILE, Dispatcher
import paho.mqtt.client as mqtt
from Lcd import lcd
import json

def glob_list(d, start=""):
    if type(d) is dict:
        for k, v in d.items():
            yield from glob_list(v, start=start+f"{k}")
    elif type(d) is list:
        if start:
            start += "/"
        for k in d:
            yield from glob_list(k, start=start)
    else:
        yield f"{start}{d}" # forever string

def get_mqtt_client(mqtt_info, tls = False):
    print("creating new mqtt_client")
    client = mqtt.Client(mqtt_info["name"])  # create new instance
    if tls:
        client.tls_set(mqtt_info["cert"], tls_version=2)
    client.username_pw_set(mqtt_info["username"], mqtt_info["password"])
    print("connecting to broker")
    client.connect(mqtt_info["broker_address"], port=mqtt_info["port"])  # connect to broker
    return client

def main():
    settings = get_settings(SETTINGS_FILE)
    mqtt_settings = settings["mqtt"]
    mqtt_client = get_mqtt_client(mqtt_settings, tls = "cert" in mqtt_settings)
    screen = lcd()

    def callback_print(print_str):
        """callback for lcd screen"""

        screen.lcd_clear()
        screen.lcd_print_lines(print_str)

    dispatcher = Dispatcher(settings["show_time"], settings["default_time"], callback_print)

    def callback(client, userdata, message):
        """calback for mqtt client on_message"""

        message = message.payload.decode("utf-8")
        msg = None
        print(f"incomed message! {message}")
        try:
            msg = json.loads(message)
        except Exception as ex:
            print(ex)
        print(f"msg: {msg}")
        if msg and "txt" in msg and "id" in msg:
            dispatcher.put_message(msg)

    print("there MQTT topics will be listen:")
    for topic in glob_list(settings["topics"]):
        print(topic)
        mqtt_client.subscribe(topic)
    mqtt_client.on_message = callback
    mqtt_client.loop_forever()



if __name__ == '__main__':
    main()
