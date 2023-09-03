import os

class HostnameChanger:
    def __init__(self):
        self.current_hostname = os.uname().nodename

    def display_current_hostname(self):
        print(f"Current hostname: {self.current_hostname}")

    def change_hostname(self):
        new_hostname = input("Enter the new hostname: ")
        confirm = input(f"Is '{new_hostname}' the hostname you want? (yes/no): ")
        while confirm.lower() != "yes":
            new_hostname = input("Enter the new hostname: ")
            confirm = input(f"Is '{new_hostname}' the hostname you want? (yes/no): ")
        # Change the hostname using the bash commands
        os.system(f"sudo hostnamectl set-hostname {new_hostname}")
        print("Hostname changed. Please reboot your Raspberry Pi for the changes to take effect.")

    def userQueryHostnameChange(self):
        self.display_current_hostname()
        change_request = input("Would you like to change the hostname? (Y/n): ")
        if change_request == "Y":
            self.change_hostname()
