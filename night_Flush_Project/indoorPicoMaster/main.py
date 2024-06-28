import time                   # Allows use of time.sleep() for delays
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
import random                 # Random number generator
from machine import Pin       # Define pin
from machine import Pin, PWM  # Used for the RG LED
import keys                   # Contain all keys used here
import wifiConnection         # Contains functions to connect/disconnect from WiFi 
import dht                    # dht temperature and humidity sensor
import nightFlushLogic         # importing the code
import uos

#Declaring global variables for house climatic automation
latestOutTemp = 23.0
latestInTemp = 23.0
forecast = 23.0
windowIsOpen = False
actionMsg = ""

"""
Information about door status and weather forecast is sent sporadically therefore
we save it to memory and load it, this in case we reset the Raspberry pi pico.
"""
def saveForecast(data, filename = "savedForecast.txt"):
    with open(filename, "w") as file:
        file.write(str(data))

def loadForecast(filename = "savedForecast.txt"):
    global forecast
    try: 
        with open(filename, "r") as file:
            forecast = float(file.read())
    except (OSError, ValueError):
        #File not found or read error. 
        return 
def saveWindowsStatus (data, filename = "savedWindowsStatus.txt"):
    with open(filename, "w") as file:
        file.write(str(data))

#Default is set to False (closed) so we only load if it is True (open)
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


# BEGIN SETTINGS
loadForecast()
loadWindowsStatus()
RANDOMS_INTERVAL = 300000    # milliseconds
last_random_sent_ticks = 0  # milliseconds
led = Pin("LED", Pin.OUT)   # led pin initialization for Raspberry Pi Pico W
led.off()
#Variables for the temperature
tempSensor = dht.DHT11(machine.Pin(27))     # DHT11 Constructor 

# Try WiFi Connection, write error code if exception happens
try:
    ip = wifiConnection.connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")
except Exception as e:
    print("Failed to connect to WiFi:", e)

# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(keys.AIO_CLIENT_ID, keys.AIO_SERVER, keys.AIO_PORT, keys.AIO_USER, keys.AIO_KEY)

def on_message(topic, msg):
    print("message received from: ", topic)
    #decode byte string from the msg:
    if topic == b'h_kenshin21/feeds/smhi':
        decoded_string = msg.decode('utf-8')
        global forecast 
        forecast = float(decoded_string)
        saveForecast(forecast)
        for duty in range(0,65_536, 1):
            red_pwm_pin.duty_u16(duty)
        for duty in range(65_536,0, -1):
            red_pwm_pin.duty_u16(duty)
        print(forecast)
    
    if topic == b'h_kenshin21/feeds/outtemp':
        decoded_string = msg.decode('utf-8')
        global latestOutTemp 
        latestOutTemp = float(decoded_string)
        for duty in range(0,65_536, 1):
            green_pwm_pin.duty_u16(duty)
        for duty in range(65_536,0, -1):
            green_pwm_pin.duty_u16(duty)
        print(latestOutTemp)
    
    if topic == b'h_kenshin21/feeds/winisopen':
        decoded_string = msg.decode('utf-8')
        global windowIsOpen
        if decoded_string == "True":
            windowIsOpen = True
        else:
            windowIsOpen = False
        saveWindowsStatus(decoded_string)
        for duty in range(0,65_536, 1):
            red_pwm_pin.duty_u16(duty)
        for duty in range(65_536,0, -1):
            red_pwm_pin.duty_u16(duty)
        for duty in range(0,65_536, 5):
            green_pwm_pin.duty_u16(duty)
        for duty in range(65_536,0, -5):
            green_pwm_pin.duty_u16(duty)
        print("Window is open: ", windowIsOpen)

    return
# Set the callback function
client.set_callback(on_message)

#RG LED
LED_Pin_Red = 22
LED_Pin_Green = 26
red_pwm_pin = PWM(Pin(LED_Pin_Red, mode=Pin.OUT)) 
green_pwm_pin = PWM(Pin(LED_Pin_Green, mode=Pin.OUT)) 

# RG LED Settings
red_pwm_pin.freq(1_000)
green_pwm_pin.freq(1_000)

def getReadings():
    global latestInTemp
    try:
        tempSensor.measure()
        innerTemp = tempSensor.temperature()
        latestInTemp = innerTemp
        innerHumidity = tempSensor.humidity()
        #print("Inner temperature is {} C and Humidity is {}%".format(innerTemp, innerHumidity))
        
    except Exception as error:
        print("Exception occurred", error)

    return innerTemp, innerHumidity
# Checks which msg to send, send only if it is a new one (different from before)
def checkActionMsg():
    global actionMsg
    oldMsg = actionMsg
    print("---\nWindow is open = ", windowIsOpen)
    newMsg = nightFlushLogic.actionMessage(windowIsOpen, forecast,latestInTemp,latestOutTemp)

    if oldMsg != newMsg:
        actionMsg = newMsg
        return newMsg
    return ""   

# Function to publish to Adafruit IO MQTT server
def sendActionMsg(feed):
    #CheckActionMsg() returns a string if the action is new, otherwhise it's an empty string
    newMsg = checkActionMsg()
    #Check if the newMsg is not empty, if so, send it
    if newMsg:
        print("Publishing:\n{0} \nto: {1} ... ".format(newMsg, feed), end='')
        try:
            client.publish(topic=feed, msg=newMsg)
        except Exception as e:
            print("FAILED")

# Function to publish to Adafruit IO MQTT server at fixed interval
def send_data(tempFeed, tempData, humFeed, humData):
    global last_random_sent_ticks
    global RANDOMS_INTERVAL

    if ((time.ticks_ms() - last_random_sent_ticks) < RANDOMS_INTERVAL):
        #print("time to next still under 300000", (time.ticks_ms() - last_random_sent_ticks))
        return; # Too soon since last one sent.

    print("Publishing:\n {0} degrees celcius to {1} and \n {2} percent humidity to {3}... ".format(tempData, tempFeed, humData, humFeed), end='')
    try:
        client.publish(topic=tempFeed, msg=str(tempData))
        client.publish(topic=humFeed, msg=str(humData))
        led.on()
        time.sleep(1)
        led.off()
        print("DONE")
        
    except Exception as e:
        print("FAILED")
    finally:
        last_random_sent_ticks = time.ticks_ms()

def connectAndSend():
    # Subscribed messages will be delivered to this callback
    global client
    client.connect()
    # subscribe to weather data
    client.subscribe(('h_kenshin21/feeds/smhi'))
    client.subscribe(('h_kenshin21/feeds/outtemp'))
    client.subscribe(('h_kenshin21/feeds/winisopen'))
    
    try:                     # Code between try: and finally: may cause an error
                            # so ensure the client disconnects the server if
                            # that happens.
        while True:         # Repeat this loop forever
            tempData, humData = getReadings()
            send_data(keys.AIO_IN_TEMP_FEED, tempData, keys.AIO_IN_HUMIDITY_FEED, humData) # Send temperature and humidity to Adafruit
            client.check_msg()
            sendActionMsg(keys.AIO_ACTION_MSG_FEED)
            time.sleep(15)
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
        
connectAndSend()