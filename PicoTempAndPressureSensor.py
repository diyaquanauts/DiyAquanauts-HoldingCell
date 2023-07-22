#  DS18X20 Temperature Sensor Imports
import time
import board
from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20

#  ADS1115 ADC Sensor Imports
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

#  Conversion Vars
SALTWATER = 1023.6
FRESHWATER = 997.0474
AIR = 1.293
GRAVITY = 9.80664
REFERENCE_VOLTAGE = 5
MAX_ADC_BITS = 32678

MIN_PRESSURE_VOLTS = 0.5  # Smallest valid voltage reading for 0 psi
MAX_PRESSURE_VOLTS = 4.5  # Largest valid voltage reading for max psi
MAX_PRESSURE_PSI = 30  # Max rating for psi

#  Init the ADS1115...
adsSCL = board.GP1
adsSDA = board.GP0
adsA0 = ADS.P0
adsA1 = ADS.P1
adsA2 = ADS.P2
adsA3 = ADS.P3

i2c = busio.I2C(adsSCL, adsSDA)
ads = ADS.ADS1115(i2c)

# Set the gain to the 6v range...
ads.gain = 2/3

# Assign the channels...
adsChannel0 = AnalogIn(ads, adsA0)
adsChannel1 = AnalogIn(ads, adsA1)
adsChannel2 = AnalogIn(ads, adsA2)
adsChannel3 = AnalogIn(ads, adsA3)

# Initialize one-wire bus on the given pin...
ow_bus = OneWireBus(board.GP5)

# Scan for sensors and grab the first one found.
ds18 = DS18X20(ow_bus, ow_bus.scan()[0])

last_time = time.monotonic()

#  Probably can get rid of this one, but the 1v difference
#  between the conversion and the native reading is weird...
def adcValueToVolts(adcValue):
    volts = (adcValue * REFERENCE_VOLTAGE) / MAX_ADC_BITS

    return volts

#  Can't for the life of me remember where I stole this from...
def adcVoltageToPSI(adcVoltageValue):
    #  P=PR∗(Vr−Vl)/(Vu−Vl)
    #  Where P is the Pressure From Voltage (psi)
    #  PR is the pressure range (psi) 
    #  Vr is the voltage reading (volts) 
    #  Vl is the voltage lower limit (volts) 
    #  Vu is the voltage upper limit (volts)
    pressureValue = (
        MAX_PRESSURE_PSI * (adcVoltageValue - MIN_PRESSURE_VOLTS) / (MAX_PRESSURE_VOLTS - MIN_PRESSURE_VOLTS)
    )

    return pressureValue


#  Using the simple formula per the Blue Robotics depth calculator:
#          https://bluerobotics.com/learn/pressure-depth-calculator/
def psiToDepth(psiReading, fluidDensity):
    depth = (psiReading) / fluidDensity * GRAVITY

    return depth


###################################################
#  Main loop to print the data every 2 seconds...
###################################################
while True:
    #  Grab the temperature...
    cTemp = ds18.temperature
    #  Convert to Farenheit...
    fTemp = cTemp * 9 / 5 + 32
    
    #  Grab the pressure sensor ADC value...
    rawAdcVal = adsChannel0.value
    
    #  Grab the pressure sensor voltage...
    voltage = adsChannel0.voltage
    
    #  Convert the ADC value to Volts...
    rawVolts = adcValueToVolts(rawAdcVal)

    #  Convert the voltage to PSI, but using
    #  the internal voltage per the ADS unit...
    pressurePSI = adcVoltageToPSI(voltage)
    
    #  Calc a +/- range...
    pressurePSI2up = pressurePSI * 1.02
    pressurePSI2down = pressurePSI * 0.98
    
    #  Print stuff...
    print(
        "\n"
        +"Temperature: {0:0.3f}C".format(cTemp)
        + " -- {0:0.3f}F".format(fTemp)
    )
    print(
        "ADC values: "
        + str(adsChannel0.value)
        + " - {0:0.2f}v".format(voltage)
        #  + " *VS* {0:0.2f}v".format(rawVolts)
        + " <--> {0:0.2}psi [ {1:0.3}psi ~ {2:0.3}psi ]".format(pressurePSI, pressurePSI2up, pressurePSI2down)
    )
    
    #  Calc the depth for air...
    airDepth = psiToDepth(pressurePSI, AIR)
    airDepth2up = airDepth * 1.02
    airDepth2down = airDepth * 0.98
    
    #  Calc the depth for saltwater...
    saltDepth = psiToDepth(pressurePSI, SALTWATER)
    saltDepth2up = saltDepth * 1.02
    saltDepth2down = saltDepth * 0.98
    
    #  Calc the depth for freshwater...
    freshDepth = psiToDepth(pressurePSI, FRESHWATER)
    freshDepth2up = freshDepth * 1.02
    freshDepth2down = freshDepth * 0.98

    #  Print more stuff...
    print(
        "Altitude -- Air: {0:0.2f}m [ {1:0.4f}m ~ {2:0.4f}m ]".format(airDepth, airDepth2up, airDepth2down)
        + "\nSaltwater: {0:0.2f}m [ {1:0.4f}m ~ {2:0.4f}m ]".format(saltDepth, saltDepth2up, saltDepth2down)
        + "\nFreshwater: {0:0.2f}m [ {1:0.4f}m ~ {2:0.4f}m ]".format(freshDepth, freshDepth2up, freshDepth2down)
    )
    
    #  NIGHTY NIGHT!
    time.sleep(4)
