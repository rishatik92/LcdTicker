# LcdTicker

simple implemetion of lcd i2c ticker for raspberry pi and mqtt.

## running on python3.6 or higher
Required Libraries:
- ruamel.yaml
- paho-mqtt
- smbus2

## using:
### send to listening topic json message with: "id","txt" and (not required "expire" in posix time):

#### topic: lcd/common/messages/status
#### {"txt":"test message", "id":"Hass"}
