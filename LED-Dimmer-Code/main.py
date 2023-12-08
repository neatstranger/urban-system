"""
A simple example that connects to the Adafruit IO MQTT server
and publishes values that represent a sine wave
"""

import network
import time
from math import sin
from umqtt.simple import MQTTClient
import machine

strip = machine.Pin(0)
strip_brightness = machine.PWM(strip)
strip_brightness.freq(1000)

led = machine.Pin("LED", machine.Pin.OUT)
brightness = 0
# So that we can respond to messages on an MQTT topic, we need a callback
# function that will handle the messages.
def mqtt_subscription_callback(topic, message):
    print (f'Topic {topic} received message {message}')  # Debug print out of what was received over MQTT
    if topic == b'neatstranger/feeds/brightness':
        brightness = (int(message)/100)*1023
        strip_brightness.duty(brightness)
        print(strip_brightness)
    if message == b'ON':
        print("LED ON")
        led.value(1)
        strip_brightness.duty(brightness)
    elif message == b'OFF':
        print("LED OFF")
        led.value(0)
        strip_brightness.duty(0)
        
def blink(count):
    x = 0
    while x <= count:
        led.value(1)
        time.sleep(0.5)
        led.value(0)
        time.sleep(0.5)
        x += 1
# Fill in your WiFi network name (ssid) and password here:
wifi_ssid = "xx"
wifi_password = "xx"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    blink(3)
    time.sleep(5)
print("Connected to WiFi")


# Fill in your Adafruit IO Authentication and Feed MQTT Topic details
mqtt_host = "io.adafruit.com"
mqtt_username = "xx"  # Your Adafruit IO username
mqtt_password = "xx"  # Adafruit IO Key

# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = "xx"

# Initialize our MQTTClient and connect to the MQTT server
mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password)
mqtt_client.set_callback(mqtt_subscription_callback)
mqtt_client.connect()
mqtt_client.subscribe("neatstranger/feeds/led")
mqtt_client.subscribe("neatstranger/feeds/brightness")
# Publish a data point to the Adafruit IO MQTT server every 3 seconds
# Note: Adafruit IO has rate limits in place, every 3 seconds is frequent
#  enough to see data in realtime without exceeding the rate limit.
counter = 0
try:
    while True:
        mqtt_client.check_msg()
        # Delay a bit to avoid hitting the rate limit
        blink(1)
        time.sleep(1)
except Exception as e:
    print(f'Failed to publish message: {e}')
finally:
    mqtt_client.disconnect()

