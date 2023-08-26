from stringer import stringer
import subprocess

class audioInput:
    def __init__(self):
        pass

    def listHardware(self):
        try:
            output = subprocess.check_output(['arecord', '-l'], universal_newlines=True)
            devices = []
            lines = output.splitlines()

            deviceInfo = ""
            subchannel = ""
            deviceName = ""

            stringUtil = stringer()

            for line in lines:
                if(line.strip().startswith("card")):
                    deviceInfo = stringUtil.getBetween(line, "card", ":")
                    subChannel = stringUtil.getBetween(line, "device", ":")
                    deviceName = stringUtil.getBetween(line, "[", "]")
                    devices.append(f"plughw:{deviceInfo},{subChannel} [{deviceName}]")

            return devices

        except subprocess.CalledProcessError as e:
            print("Error listing audio recording hardware:", e)
            return []

if __name__ == "__main__":
    audioDevices = audioInput.listHardware()

    if audioDevices:
        for device in audioDevices:
            print(device)
    else:
        print("No audio recording hardware found.")
