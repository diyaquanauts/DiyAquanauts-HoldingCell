import win32com.client

# Initialize the WMI interface
wmi = win32com.client.GetObject('winmgmts:')

cameras = []

# Query for all devices
for device in wmi.InstancesOf('Win32_PnPEntity'):
    print(f'Device Name: {device.Name}, Device ID: {device.DeviceID}')
    test = f'{device.Name} -- {device.DeviceID}'
    if test.find("Camera") > 0 or test.find("Camera") > 0:
        cameras.append(test)


for camera in cameras:
    print(camera)
