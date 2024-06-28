import ubinascii
import machine
# Wireless network: Your WiFi Credentials
WIFI_SSID = 'Your_wifi_SSID'
WIFI_PASS = 'Your_wifi_Password' 

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_USER = "your_user_name_here"
AIO_KEY = "your_aio_key_here"

AIO_WINDOW_STATUS_FEED = "your_feed_MQTT" # Looks like this format: "user_name/feeds/winisopen"
