import time                   # Allows use of time.sleep() for delays
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
from machine import Pin       # Define pin
import keys                   # Contain all keys used here
import wifiConnection         # Contains functions to connect/disconnect from WiFi 
import dht                    # dht temperature and humidity sensor

# BEGIN SETTINGS
client = None
RANDOMS_INTERVAL = 300000   # milliseconds (5 min)
last_random_sent_ticks = 0  # milliseconds
led = Pin("LED", Pin.OUT)   # led pin initialization for Raspberry Pi Pico W
led.off()
#Variables for the temperature
tempSensor = dht.DHT11(machine.Pin(27))     # DHT11 Constructor 

#Reads temperature and humidity returns both variables
def getReadings():
    try:
        tempSensor.measure()
        outTemp = tempSensor.temperature()
        outHumidity = tempSensor.humidity()
        print("Outdoors temperature is {} C and Humidity is {}%".format(outTemp, outHumidity))
    except Exception as error:
        print("Exception occurred", error)

    time.sleep(1)
    return outTemp, outHumidity

# Function to publish random number to Adafruit IO MQTT server at fixed interval
def send_data(tempFeed, tempData, humFeed, humData):
    global last_random_sent_ticks
    global RANDOMS_INTERVAL

    if ((time.ticks_ms() - last_random_sent_ticks) < RANDOMS_INTERVAL):
        # If it is too soon since last one sent, goes back to the loop
        print((time.ticks_ms() - last_random_sent_ticks), "Too soon")
        return;

    print("Publishing:\n {0} degrees celcius to {1} and \n {2} percent humidity to {3}... ".format(tempData, tempFeed, humData, humFeed), end='')
    try:
        print(tempFeed, tempData)
        client.publish(topic=tempFeed, msg=str(tempData))
        client.publish(topic=humFeed, msg=str(humData))
        print("DONE")
        
    except Exception as e:
        print("FAILED")
    finally:
        last_random_sent_ticks = time.ticks_ms()

def connectAndSend():
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
    
    try:                    # Code between try: and finally: may cause an error
                            # so ensure the client disconnects the server if
                            # that happens.
        while True:         # Repeat this loop forever
            tempData, humData = getReadings()
            print("attempting to send...")
            led.on()
            time.sleep(5)
            led.off()
            time.sleep(1)
            send_data(keys.AIO_OUT_TEMP_FEED, tempData, keys.AIO_OUT_HUMIDITY_FEED, humData) # Send temperature and humidity to Adafruit
            time.sleep(4)
    finally:                  # If an exception is thrown ...
        client.disconnect()   # ... disconnect the client and clean up.
        client = None
        wifiConnection.disconnect()
        print("Disconnected from Adafruit IO.")
        
connectAndSend()
