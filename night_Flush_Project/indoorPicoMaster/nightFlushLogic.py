
#Logic to switch fan on/off. Sensor to know if it is on? (vibrating?)
# OPTIONAL: def checkBoostButton() #if pressed then pointTask is -2 degrees
  
setPointTemp = 23
# Calculate setpoint temperature based on forecast.
# For hot days we want cooler indoor temperature to lower risk of overheating during the day
# Todo: if time, add button for booster (add boolean that lowers the setpoint 2 degrees)
def calculateSetPoint(forecast):
    global setPointTemp
    if forecast>27:
        setPointTemp = 21
    elif forecast >23:
        setPointTemp = 22
    else:
        setPointTemp = 23

#Checks if the forecast temperature is high. Returns a boolean (True if hot)
def checkIsHotDay(forecast):
    isHotDay = False
    if forecast>25:
        isHotDay = True
    return isHotDay

#Checks if the conditions are met for opening windows on a hot day forecast
def hotDaySetting(deltaInSet, deltaInOut):
    openWindow = False
    '''On a hot day forecast, check these two conditions and return a boolean (openWindow = True) if both are met:
        * temperature indoors - setPoint temperature (desired temperature) is larger than zero
        * temperature indoors - temperature outdoors is larger than zero '''
    if deltaInSet>0 and deltaInOut>0:
        openWindow = True
    return openWindow

#Checks if the conditions are met for opening the windows on a cool day forecast
#The reason being, if the indoor temperature is much higher, we may want to cool it down a bit
def coolDaySetting(deltaInSet, deltaInOut):
    openWindow = False
    '''On a cool day forecast, check these two conditions and return a boolean (openWindow = True) if both are met:
        * temperature indoors - setPoint temperature (desired temperature) is larger than 2 (so it has to be 3 or more)
        * temperature indoors - temperature outdoors is larger than zero '''    
    if deltaInSet>2 and deltaInOut>0:
        openWindow = True
    return openWindow

#Check if nightFlush is necessary (if windows should be opened) returns a boolean
def checkNightFlush(forecast, tempIn, tempOut):
    calculateSetPoint(forecast)

    #Print out data:
    print("""---\nForecast temperature:{0} C//Indoor: {1} C//Desired: {2}C//Outdoor: {3} C")\n---""".format(forecast, tempIn, setPointTemp, tempOut))
    
    #Delta T in -set = temperature indoors - desired temperature
    deltaTinSet = tempIn - setPointTemp
    
    #Delta T in-out temperature indoors - temperature outdoors
    deltaTinOut = tempIn - tempOut
    
    if checkIsHotDay(forecast):
        openWindow = hotDaySetting(deltaTinSet, deltaTinOut)
    else:
        openWindow = coolDaySetting(deltaTinSet, deltaTinOut)
    return openWindow

#Send msg to open or close the windows based on data
def actionMessage(windowIsOpen, forecast, tempIn, tempOut):
    calculateSetPoint(forecast)
    nightFlush = checkNightFlush(forecast, tempIn, tempOut)

    if not windowIsOpen and nightFlush:
        #code for action - open the window
        msg = """Conditions for night-flush are good:
        tomorrow's max-temp is going to be = {0} C,
        indoor temperature = {1} C (desired temperature = {2} C)
        outdoor temperature = {3}
        Open windows for night-flushing""".format(forecast, tempIn, setPointTemp, tempOut )        
    
    elif windowIsOpen and nightFlush:
        msg = "Night-flush ON (window is open)"

    elif windowIsOpen and not nightFlush:
        #code for action - close the window
        msg = """Conditions for night-flush are not optimal:
        tomorrow's max-temp is going to be = {0} C,
        indoor temperature = {1} C (desired temperature = {2} C)
        outdoor temperature = {3} 
        Close windows to avoid overtemperatures""".format(forecast, tempIn, setPointTemp, tempOut )     

    else:
        msg = "Night-flush OFF (window is closed)"    
    
    return msg

