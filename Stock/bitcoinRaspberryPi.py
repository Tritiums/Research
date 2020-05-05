#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
from exchanges.bitfinex import Bitfinex
import lcddriver
import time


# In[ ]:


display = lcddriver.lcd()


# In[ ]:


while(True):
    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    
    bitcoin = Bitfinex().get_current_price()
    price = float(bitcoin)

    #humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 17)

    # Un-comment the line below to convert the temperature to Fahrenheit.
    # temperature = temperature * 9/5.0 + 32

    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    # If this happens try again!


    if price is not None:
        print(price)
        
        display.lcd_display_string("Bitcoin: " + str(price), 1) # Write line of text to first line of display
        #display.lcd_display_string("Humidity: " + str(humidity) +'% ', 2) # Write line of text to second line of display
        time.sleep(1)                                     # Give time for the message to be read
        #display.lcd_clear()                
    else:
        print('Failed to get reading. Try again!')
        sys.exit(1)

