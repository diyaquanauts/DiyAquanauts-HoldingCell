# Power Timer
This folder contains the installation scripts and runtime methods to use the buoys custom power timer PCB.
# scheduleWakeup.py

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

This uses adafruit circuit python ds3231:
https://github.com/adafruit/Adafruit_CircuitPython_DS3231  
Which relies heavily on:  
https://github.com/adafruit/Adafruit_CircuitPython_Register


# configure_rtc.sh 
A script to install and configure the DS3231 Real Time Clock (RTC) as the Raspberry Pis hardware rtc.

### Usage
```bash
sudo bash configureRtc.sh
```

### What does the script do?
1. Synchronizes the Raspberry Pi with NTP servers to ensure accurate system time.
2. Removes the fake-hwclock package and its associated services.
3. Modifies the boot configuration to enable the DS3231 RTC module.
4. Sets up the DS3231 RTC module with the current system time.

# configure_gpio.sh

This script ensures that the GPIO 17 configuration for both boot and poweroff is set up correctly in the `/boot/config.txt` file on a Raspberry Pi. 

### Script Overview

This script is used to enable GPIO 17 as the "power hold" line for the buoys custom power management board.

1. Check if GPIO 17 boot configuration exists in the `config.txt` file.
2. If not found, it adds the required configuration line for GPIO 17 boot.
3. Check if GPIO 17 poweroff configuration exists in the `config.txt` file.
4. If not found, it adds the required configuration line for GPIO 17 poweroff.
5. Outputs a message to inform the user that the configuration is complete and a reboot is needed to apply changes.

### Usage

To run the script:

```bash
chmod +x configure_gpio.sh
sudo ./configure_gpio.sh