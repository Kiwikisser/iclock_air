import os, bluetooth, subprocess, serial, time, threading, sys, datetime, pytz
from flask import Flask, redirect, url_for, render_template, request
import RPi.GPIO as GPIO

################################ HX711 SETUP ################################

sys.path.append('/home/pi/flask/hx711py')
from hx711 import HX711

#ck dt
hx1 = HX711(5, 6)
hx2 = HX711(20, 16)
hx3 = HX711(19, 13)
hx4 = HX711(22, 27)

hx1.set_reading_format("MSB", "MSB")
hx2.set_reading_format("MSB", "MSB")
hx3.set_reading_format("MSB", "MSB")
hx4.set_reading_format("MSB", "MSB")

hx1.set_reference_unit(2.959)
hx2.set_reference_unit(2.959)
hx3.set_reference_unit(2.959)
hx4.set_reference_unit(2.959)

hx1.reset()
hx2.reset()
hx3.reset()
hx4.reset()

hx1.tare()
hx2.tare()
hx3.tare()
hx4.tare()

print("Tare done!")

################################ ALARM OBJECT ################################

class Alarm:
  def __init__(self, alarmTime):     # maybe (self, hours, minutes) ?
    self.alarmTime = alarmTime

  def setTime(time):
    self.alarmTime = alarmTime

  def getTime():
    return alarmTime

# p1 = Person("John", 36)
# p1.myfunc()

################################ BT CONNECTION ################################

if os.path.exists('/dev/rfcomm0') == False:
    path = 'sudo rfcomm bind 0 98:D3:31:F5:9A:3C'
    os.system (path)
    time.sleep(1)

bluetoothSerial = serial.Serial( "/dev/rfcomm0", baudrate=9600 )

count = 4

j = str(count)
b = j.encode()
bluetoothSerial.write(b)

################################ CACHE FIX ################################

app = Flask(__name__)

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

################################ WEB ROUTES ################################

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        alarmTime = request.form["time"]
        print("time is set to: ")
        print(alarmTime)
        return render_template("index.html", last_updated=dir_last_updated('static'), content=alarmTime)
    else:
        return render_template("index.html", last_updated=dir_last_updated('static'))

################################ TIME CHECKING ################################

# now = datetime.now()
#
# timestamp = datetime.timestamp(now)
# print("timestamp =", timestamp)

startTime = time.time()
interval = 20
# print("Seconds since epoch =", seconds)

def cleanAndExit():
print("Cleaning...")

if not EMULATE_HX711:
    GPIO.cleanup()

print("Bye!")
sys.exit()

def checkTime( threadName, interval):
    cumulativeInterval = 0
    while True:
        try:
            val1 = hx1.get_weight(5)
            val2 = hx2.get_weight(5)
            val3 = hx3.get_weight(5)
            val4 = hx4.get_weight(5)
            print("Sensor 1: %s,\t 2: %s,\t 3: %s,\t 4: %s" % (val1, val2, val3, val4))

            hx1.power_down()
            hx1.power_up()
            hx2.power_down()
            hx2.power_up()
            hx3.power_down()
            hx3.power_up()
            hx4.power_down()
            hx4.power_up()
            time.sleep(0.1)     #obsolete

            time.sleep(interval)
            cumulativeInterval = cumulativeInterval + interval

            print( threadName, time.ctime(time.time()) )
            # get time with % secons_in_day?
            # compare daily timestamps? lib?
            if cumulativeInterval % 60 == 0:
                # check if person on bed
                # go off if

        except (KeyboardInterrupt, SystemExit):
            cleanAndExit()

try:
    alarm = threading.Thread(target=checkTime, args=("alarmThread", 5,))
    alarm.start()
except:
   print("unable to start thread")

################################ MAIN LOOP ################################


################################ MAIN LOOP ################################

if __name__ == "__main__":
    # try:
        app.run(host= '0.0.0.0', debug=True)

        # elapsedTime = time.time()
        # if elapsedTime - startTime > interval:
        #     startTime = elapsedTime
        #     print("interval called")

    # except (KeyboardInterrupt, SystemExit):
    	# print('Bye :)')
#
    # finally:
    	# GPIO.cleanup()
