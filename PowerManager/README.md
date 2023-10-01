This uses adafruit circuit python ds3231:
https://github.com/adafruit/Adafruit_CircuitPython_DS3231
Which relies heavily on:
https://github.com/adafruit/Adafruit_CircuitPython_Register


Things we have to do to get this ready:
1. Update the boot config so GPIO 17 is always high when the pi is on, but turns off after a shtudown.

In boot/config.txt
gpio=17=op,dh
gpio-poweroff=gpiopin=17,active_low

## scheduleWakeup.py

This script allows users to set an alarm on a DS3231 RTC module connected to a Raspberry Pi. The alarm can be set to trigger in seconds, minutes, hours, or days.

### Requirements

- Python 3.x
- Libraries:
  - `board`
  - `busio`
  - `adafruit_ds3231`

### Installation

1. Ensure you have Python 3.x installed.
2. Install required libraries:
```bash
pip install adafruit-circuitpython-ds3231
```

### Usage
Run the script using Python, followed by the mode and value you'd like to set the alarm for. You can also use the --shutdown flag to shutdown the system 1 minute after setting the alarm.

```bash
python setAlarm.py [-h] -m {secondly,minutely,hourly,daily} [-v VALUE] [--shutdown]
```

## Configure RTC 
A script to install and configure the DS3231 Real Time Clock (RTC) as the Raspberry Pis hardware rtc.

### Usage
```bash
sudo bash configureRtc.sh
```

### What does the script do?
