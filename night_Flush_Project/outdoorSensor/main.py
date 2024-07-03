import time                   # Allows use of time.sleep() for delays
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import machine                # Interfaces with hardware components
from machine import Pin       # Define pin
import keys                   # Contain all keys used here
import wifiConnection         # Contains functions to connect/disconnect from WiFi 
import dht                    # dht temperature and humidity sensor

# BEGIN SETTINGS

client = None
led = Pin("LED", Pin.OUT)   # led pin initialization for Raspberry Pi Pico W
led.off()
#Variables for the temperature
tempSensor = dht.DHT11(machine.Pin(27))     # DHT11 Constructor 

import wifiConnection  
import time

#Modified the code because I was having conexion issues
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

#Reads temperature and humidity returns both variables
def getReadings():
    try:
        tempSensor.measure()
        outTemp = tempSensor.temperature()
        outHumidity = tempSensor.humidity()
        print("Outdoors temperature is {} C and Humidity is {}%".format(outTemp, outHumidity))
    except Exception as error:
        print("Exception occurred", error)
        #Nonsense values can be a good indicator for sensors not working:
        outTemp, outHumidity = -50, 0
    return outTemp, outHumidity 

# Function to publish random number to Adafruit IO MQTT server at fixed interval
def send_data(tempFeed, tempData, humFeed, humData):

    print("Publishing:\n {0} degrees celcius to {1} and \n {2} percent humidity to {3}... ".format(tempData, tempFeed, humData, humFeed), end='')
    try:
        client.publish(topic=tempFeed, msg=str(tempData))
        client.publish(topic=humFeed, msg=str(humData))
        print("DONE")
        
    except Exception as e:
        print("FAILED")

def connectAndSend():
    global client 

    while True:
        # Try WiFi Connection
        try:
            connect_wifi()
            led.on()
        except KeyboardInterrupt:
            break
        except Exception as e:
            led.off()
            print("Failed to connect to Wi-Fi:", e)
            time.sleep(10)  # Wait before retrying
            continue  # Skip the rest of the loop and retry

        try:
            # Use the MQTT protocol to connect to Adafruit IO
            client = MQTTClient(keys.AIO_CLIENT_ID, keys.AIO_SERVER, keys.AIO_PORT, keys.AIO_USER, keys.AIO_KEY)
            # Subscribed messages will be delivered to this callback
            client.connect()
            print("Connected to Adafruit IO.")
        except Exception as e:
            print("Failed to connect to MQTT server:", e)
            wifiConnection.disconnect()
            led.off()
            time.sleep(10)  # Wait before retrying
            continue  # Skip the rest of the loop and retry

        try:     
            tempData, humData = getReadings()
            print("attempting to send...")
            led.off()
            time.sleep(1)
            led.on()
            time.sleep(1)
            led.off()
            time.sleep(1)
            led.on()
            # Send temperature and humidity to Adafruit
            send_data(keys.AIO_OUT_TEMP_FEED, tempData, keys.AIO_OUT_HUMIDITY_FEED, humData) 
            
        except Exception as e:
            print("Failed to send data:", e)
            led.off()
        finally:                  # If an exception is thrown ...
            if client:
                client.disconnect()
                client = None
            wifiConnection.disconnect()
            print("Disconnected from Adafruit IO.")
            led.off()
            time.sleep(1)
            led.on()
            time.sleep(240) #Wait 4 minutes before continuing the loop
        
connectAndSend()
