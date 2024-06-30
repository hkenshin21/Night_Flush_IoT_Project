
"""Logic for what is going to happen depending on the weather conditions, 
    forecast and indoor temperature """ 
#Initialize setPointTemperature to cool day settings:
setPointTemp = 23

"""Calculate setpoint temperature based on forecast.
    For hot days we want a cooler indoor temperature to 
    lower the risk of overheating during the day.
    This settings can be adjusted after some measurings"""


def calculateSetPoint(forecast):
    global setPointTemp
    """Adjust if needed
        in my case it usually gets a couple of degrees hotter
        than the forecast predicts so I adjust for that adding 2 degrees:"""
    adjustedForecast = forecast+2

    if adjustedForecast>27:
        setPointTemp = 20
    elif adjustedForecast >25:
        setPointTemp = 21
    else:
        setPointTemp = 23

#Checks if the forecast temperature is high. Returns a boolean (True if hot)
def checkIsHotDay(forecast):
    isHotDay = False
    if forecast>23:
        isHotDay = True
    return isHotDay

#Checks if the conditions are met for opening windows on a hot day forecast
def hotDaySetting(deltaInSet, deltaInOut):
    '''On a hot day forecast, check these two conditions and return a boolean (openWindow = True) if both are met:
        * temperature indoors - setPoint temperature (desired temperature) is larger than zero
        * temperature indoors - temperature outdoors is larger than zero '''
    return deltaInSet>0 and deltaInOut>0

#Checks if the conditions are met for opening the windows on a cool day forecast
#The reason being, if the indoor temperature is much higher, we may want to cool it down a bit
def coolDaySetting(deltaInSet, deltaInOut):
    '''On a cool day forecast, check these two conditions and return a boolean (openWindow = True) if both are met:
        * temperature indoors - setPoint temperature (desired temperature) is larger than 2 (so it has to be 3 or more)
        * temperature indoors - temperature outdoors is larger than zero '''    
    return deltaInSet>2 and deltaInOut>0

#Check if nightFlush is necessary (if windows should be opened) returns a boolean
def checkNightFlush(forecast, tempIn, tempOut):
    calculateSetPoint(forecast)

    #Print out data for testing:
    #print("""---\nForecast temperature:{0} C//Indoor: {1} C//Desired: {2}C//Outdoor: {3} C")\n---""".format(forecast, tempIn, setPointTemp, tempOut))
    
    #Delta T in - set = temperature indoors - desired temperature
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
        #msg= f"Open Windows for night flush: Forecast = {forecast} C, T-in = {tempIn} C, Set = {setPointTemp} C, T-out = {tempOut} C"
        msg = "Open the windows"
    elif windowIsOpen and nightFlush:
        msg = "Airing ON (window is open)"
    elif windowIsOpen and not nightFlush:
        #code for action - close the window
        #msg = f"Close Windows to stop night flush: Forecast = {forecast} C, T-in = {tempIn} C, Set = {setPointTemp} C, T-out = {tempOut} C"
        msg = "Close the windows"    
    else:
        msg = "Airing OFF (window is closed)"    
    return msg

