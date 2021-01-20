import os, bluetooth, subprocess, serial, time
from flask import Flask, redirect, url_for, render_template, request
from datetime import datetime
import RPi.GPIO as GPIO

class Alarm:
  def __init__(self, alarmTime):     # maybe (self, hours, minutes) ?
    self.alarmTime = alarmTime

  def setTime(time):
    self.alarmTime = alarmTime

  def getTime():
    return alarmTime

# p1 = Person("John", 36)
# p1.myfunc()

if os.path.exists('/dev/rfcomm0') == False:
    path = 'sudo rfcomm bind 0 98:D3:31:F5:9A:3C'
    os.system (path)
    time.sleep(1)

bluetoothSerial = serial.Serial( "/dev/rfcomm0", baudrate=9600 )

# global alarmTime
# alarmTime = 8

count = 4

j = str(count)
b = j.encode()
bluetoothSerial.write(b)

app = Flask(__name__)

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        alarmTime = request.form["time"]
        print("time is set to: ")
        print(alarmTime)
        return render_template("index.html", last_updated=dir_last_updated('static'), content=alarmTime)
    else:
        return render_template("index.html", last_updated=dir_last_updated('static'))

# now = datetime.now()
#
# timestamp = datetime.timestamp(now)
# print("timestamp =", timestamp)

startTime = time.time()
interval = 20
# print("Seconds since epoch =", seconds)

def checkTime( threadName, interval):
  time.sleep(interval)
  print( threadName, time.ctime(time.time()) )

try:
   thread.start_new_thread( checkTime, ("Alarm-Thread", 5, ) )
except:
   print("Error: unable to start thread")


if __name__ == "__main__":
    # try:
        app.run(host= '0.0.0.0', debug=True)

        elapsedTime = time.time()
        if elapsedTime - startTime > interval:
            startTime = elapsedTime
            print("interval called")

    # except (KeyboardInterrupt, SystemExit):
    	# print('Bye :)')
#
    # finally:
    	# GPIO.cleanup()
