# Night_Flush_IoT_Project
EcoCool: Energy-Saving With Night Ventilation (Night Flush)

This project is the result of an assignment from the Summercourse *Introduction to Applied IoT, Summer of 2024*

The project is a proof of concept for a night cooling system. My goal is to use the nights cooler air to remove the heat that builds up in buildings during hot summer days. By doing this, we can save energy, wa can reduce the need for air conditioning, and in some cases we might not need an AC system at all. 

The setup needs indoor and outdoor temperature sensors, a sensor to check if the window(s) are open or closed and forecast data to set a desired indoor temperature based on next days maximum temperature. If the next day will be hot, then we get a signal to open the windows to air the house, provided the outdoor temperature is lower than the indoor temperature. When the outdoor temperature starts to rise again during the morning, the system sends a signal (a message to my phone) to close the windows. 

This setting can be modified to control an exhaust fan instead, then the signal can check the fans speed and adjust accordingly, maxing the speed durig night flush and minimizing it during hot summer days. 

 A complete guide on the project can be found here: 
 <a href ="https://hackmd.io/@0eE0qrw8QBKeNwBeNTenTQ/ry1lWNvUC" >My Hackmd</a>

We need some external libraries, all are in the repository (so you can just copy-paste all to your own project) but the original code can be found in these repositories: 

* <a href= "https://github.com/iot-lnu/applied-iot/blob/master/Pycom%20Micropython%20(esp32)/network-examples/mqtt_ubidots/mqtt.py" >MQTTClient </a>
* <a href = "https://github.com/iot-lnu/pico-w/tree/main/network-examples/N1_WiFi_Connection"> wifiConnection</a>
 
A demo can be seen here <a href = "https://youtu.be/jSCFRoGST6Y" >Project demo Youtube</a>
