import serial
import time
from azure.iot.device import IoTHubDeviceClient, Message
# az iot hub monitor-events --hub-name 318Hub --device-id bioserde

CONNECTION_STRING = "HostName=318Hub.azure-devices.net;DeviceId=bioserde;SharedAccessKey=ml0XIrouzxoP/zmDGex1lHNjcCj76+cD/aRwKc+r9no="
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
ser = serial.Serial('COM4', 9600)

print("Connecting to Azure IoT Hub...")
client.connect()
print("Connected to Azure IoT Hub")

try:
    while True:
        print("Bytes waiting:", ser.in_waiting)
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Read from Arduino: {line}")
            msg = Message(line)
            client.send_message(msg)
            print("Message sent to IoT Hub")
            time.sleep(0.5)
        else:
            time.sleep(0.1)

finally:
    print("Disconnecting...")
    client.disconnect()
    ser.close()
