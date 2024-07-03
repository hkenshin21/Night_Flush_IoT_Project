import time                   # Allows use of time.sleep() for delays
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
from machine import Pin       # Define pin
import keys                   # Contain all keys used here
import wifiConnection         # Contains functions to connect/disconnect from WiFi 


# BEGIN SETTINGS
sensorState = False
client = None
led = Pin("LED", Pin.OUT)   # led pin initialization for Raspberry Pi Pico W
led.off()
digitalPin = Pin(27, Pin.IN)

''' Checks the sensor state - for proof of concept
its a Hall Sensor and we are detecting if a window is open or not:
checkWindow() returns a boolean, True when no magnetic field is detected'''
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

def saveWindowsStatus (data, filename = "savedWindowsStatus.txt"):
    with open(filename, "w") as file:
        file.write(str(data))
# Default when initializing is set to False (closed) so we only load if it is True (open)
def loadWindowsStatus (filename = "savedWindowsStatus.txt"):
    global windowIsOpen
    try: 
        with open(filename, "r") as file:
            stringResult = file.read()
            if stringResult == "True":
                windowIsOpen = True
    except (OSError, ValueError):
        #File not found or read error. 
        return 

# Try WiFi Connection, write error code if exception happens, useful for debugging
def connect_wifi(max_retries=5, initial_delay=2):
    for attempt in range(max_retries):
        try:
            wifiConnection.connect()
            led.on()
            return
        except Exception as e:
            print(f"Failed to connect to Wi-Fi on attempt {attempt + 1}: {e}")
            led.off()
            time.sleep(initial_delay * (2 ** attempt))  # Exponential backoff
    raise Exception("Failed to connect to Wi-Fi after multiple attempts")

# Function to publish to Adafruit IO MQTT server at fixed interval
def send_data(feed, data):
    print("Publishing:\n window open = {0} to {1} ... ".format(data, feed), end='')
    try:
        client.publish(topic=feed, msg=str(data))
        print("DONE") 
    except Exception as e:
        print("FAILED")

def connectAndSend(data):
    global client 
    # Try WiFi Connection
    try: 
        connect_wifi()
        led.on()
        if client is None:
            # Use the MQTT protocol to connect to Adafruit IO
            client = MQTTClient(keys.AIO_CLIENT_ID, keys.AIO_SERVER, keys.AIO_PORT, keys.AIO_USER, keys.AIO_KEY)
        try:
            client.connect()
            print("Connected to Adafruit IO.")
        except Exception as e:
            print("MQTT Connection error:", e)
        try:                # Code between try: and finally: may cause an error
                            # so ensure the client disconnects the server if
                            # that happens.
            print("attempting to send...")
            send_data(keys.AIO_WINDOW_STATUS_FEED, data) # Send info to Adafruit
            led.off()
            time.sleep(1)
            led.on()
            time.sleep(1)
            led.off()
            time.sleep(1)
            led.on()
            time.sleep(1)
        #Handle OSError and make automatic reconnection
        except Exception as e:
            print("Failed to send data:", e)
            led.off()

        finally:                  
            client.disconnect()   
            client = None
            wifiConnection.disconnect()
            print("Disconnected from Adafruit IO.\nDisconnected to wifi")

    except Exception as e:
            print("error from first try ", e)

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
            saveWindowsStatus(sensorState)
            print("sensorState= ", sensorState)
        else:
            print("no changes")
            time.sleep(2)
    
loadWindowsStatus()
checkStatusSendOnChange()
