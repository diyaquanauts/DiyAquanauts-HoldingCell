import os
import sys
import argparse
import board
import busio
import adafruit_ds3231
from datetime import datetime, timedelta
import time

def set_alarm(mode, value):
    i2c = busio.I2C(board.SCL, board.SDA)
    rtc = adafruit_ds3231.DS3231(i2c)

    if rtc.alarm1_status:
        rtc.alarm1_status = False

    current_time_tuple = rtc.datetime
    current_time = datetime(*current_time_tuple[:6])

    if mode == "secondly":
        alarm_time = current_time + timedelta(seconds=value)
        alarm_mode = "secondly"
    elif mode == "minutely":
        alarm_time = current_time + timedelta(minutes=value)
        alarm_mode = "minutely"
    elif mode == "hourly":
        alarm_time = current_time + timedelta(hours=value)
        alarm_mode = "hourly"
    else:  # daily
        alarm_time = current_time + timedelta(days=value)
        alarm_mode = "daily"

    alarm_struct = time.struct_time((alarm_time.year, alarm_time.month, alarm_time.day,
                                    alarm_time.hour, alarm_time.minute, alarm_time.second,
                                    -1, -1, -1))

    rtc.alarm1 = (alarm_struct, alarm_mode)

    # Here we will ensure the alarm was set correctly by checking the alarm interrupt flag
    if rtc.alarm1_interrupt:
        print(f"Alarm set for: {alarm_time.strftime('%Y-%m-%d %H:%M:%S')} Mode: {mode}")
        return True
    else:
        print("Failed to set the alarm.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Set the RTC DS3231 alarm.")
    
    parser.add_argument("-m", "--mode", 
                        choices=["secondly", "minutely", "hourly", "daily"], 
                        help="""Alarm mode:\n
                                'secondly': Set the alarm to trigger every specified seconds.\n
                                'minutely': Set the alarm to trigger every specified minutes.\n
                                'hourly': Set the alarm to trigger every specified hours.\n
                                'daily': Set the alarm to trigger every specified days.""")
    
    parser.add_argument("-v", "--value", 
                        type=int, 
                        default=1, 
                        help="Value corresponding to the mode. E.g., for '-m daily', it sets the alarm 'value' days from now. For '-m hourly', 'value' hours from now.")

    parser.add_argument("--shutdown",
                        action="store_true",
                        help="Shutdown the system after 1 minute of setting the timer.")
    
    args = parser.parse_args()

    # Display help if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    alarm_was_set = set_alarm(mode=args.mode, value=args.value)
     Check if shutdown flag is set and alarm was successfully set
    if args.shutdown and alarm_was_set:
        print("Shutting down in 1 minute. Make sure switch is set to auto or system cannot possibly wake itself up!")
        os.system("sudo shutdown -h +1")
        sys.exit()
    elif args.shutdown and not alarm_was_set:
        print("Error setting alarm. System will not shut down.")
        sys.exit(1)


if __name__ == "__main__":
    main()

