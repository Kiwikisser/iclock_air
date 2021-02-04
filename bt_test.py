import os, bluetooth, subprocess, serial, time, threading, sys, datetime, pytz
import serial.tools.list_ports


if os.path.exists('/dev/rfcomm0') == False:
    path = 'sudo rfcomm bind 0 98:D3:31:F5:9A:3C'
    os.system (path)
    time.sleep(1)

# if os.path.exists('/dev/rfcomm1') == False:
#     path = 'sudo rfcomm bind 1 00:21:13:00:44:23'
#     os.system (path)
#     time.sleep(1)
count = 7

j = str(count)
b = j.encode()

bluetoothSerial = serial.Serial( "/dev/rfcomm0", baudrate=6900 )
# bluetoothSerial = serial.Serial( "/dev/rfcomm1", baudrate=9600 )

bluetoothSerial.write(b)

if __name__ == "__main__":
    while True:
        # print(bluetoothSerial.isOpen())
        # bluetoothSerial = serial.Serial( "/dev/rfcomm0", baudrate=9600 )
        #
        # myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        # print (myports)
        # time.sleep(5)
        # bluetoothSerial.write(b)
        # time.sleep(1)
        # print(b)
        try:
            bluetoothSerial.write(b)
            print(b)
            print("in try")
            ser_bytes = bluetoothSerial.readline()
            decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
            print(decoded_bytes)
        except Exception as e:
            print(e)
            break
