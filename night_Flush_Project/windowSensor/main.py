import time                   # Allows use of time.sleep() for delays
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
from machine import Pin       # Define pin
import keys                   # Contain all keys used here
import wifiConnection         # Contains functions to connect/disconnect from WiFi 

client = None
# BEGIN SETTINGS
# Declaring fanIsOn variable
sensorState = False

led = Pin("LED", Pin.OUT)   # led pin initialization for Raspberry Pi Pico W
led.off()
digitalPin = Pin(27, Pin.IN)

''' Checks the sensor state - for proof of concept
its a Hall Sensor and we are detecting if a window is open or not:'''
def checkWindow():
    digitalValue = digitalPin.value()
    if digitalValue:
        #When no magnetic field is detected, the window is open:
        windowIsOpen = True  
        print("No magnetic field detected")
    else:
        #When a magnetic field is detected, the window is closed (the magnet on the window frame is near the sensor):
        windowIsOpen = False
        print("Magnet field detected")
    print(windowIsOpen)
    return windowIsOpen    

# Function to publish to Adafruit IO MQTT server at fixed interval
def send_data(feed, data):
    print("Publishing:\n window open = {0} to {1} ... ".format(data, feed), end='')
    try:
        client.publish(topic=feed, msg=str(data))
        print("DONE") 
    except Exception as e:
        print("FAILED")

def connectAndSend(data):
    # Try WiFi Connection
    try:
        ip = wifiConnection.connect()
    except KeyboardInterrupt:
        print("Keyboard interrupt")

    # Use the MQTT protocol to connect to Adafruit IO
    global client 
    client = MQTTClient(keys.AIO_CLIENT_ID, keys.AIO_SERVER, keys.AIO_PORT, keys.AIO_USER, keys.AIO_KEY)

    # Subscribed messages will be delivered to this callback
    client.connect()
    
    try:                # Code between try: and finally: may cause an error
                        # so ensure the client disconnects the server if
                        # that happens.
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(1)
        send_data(keys.AIO_WINDOW_STATUS_FEED, data) # Send info to Adafruit
        time.sleep(1)
    #Handle OSError and make automatic reconnection
    except OSError as e:
        print("MQTT Connection error:", e)
        time.sleep(10)  # Wait before attempting to reconnect
        connectAndSend()  # Attempt to reconnect recursively

    finally:                  # If an exception is thrown ...
        client.disconnect()   # ... disconnect the client and clean up.
        client = None
        wifiConnection.disconnect()
        print("Disconnected from Adafruit IO.")

def checkStatusSendOnChange():
    while True:
        global sensorState
        oldState = sensorState
        newState = checkWindow()
        print("old state: ", oldState)
        print("new State: ", newState)
        if oldState != newState:
            connectAndSend(newState)
            sensorState = newState
            print("sensorState= ", sensorState)
        else:
            print("no changes")
            time.sleep(15)

checkStatusSendOnChange()