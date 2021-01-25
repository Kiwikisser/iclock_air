import os, bluetooth, subprocess, serial, time, threading, sys, datetime, pytz
from flask import Flask, redirect, url_for, render_template, request
import RPi.GPIO as GPIO

app = Flask(__name__)

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
hx4.set_reference_unit(3.1)

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

  def setTime(self, alarmTime):
    self.alarmTime = alarmTime

  def getTime(self):
    return self.alarmTime

# p1 = Person("John", 36)
# p1.myfunc()

myAlarm = Alarm(9)

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

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

################################ WEB ROUTES ################################

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        # globAlarmHour = request.form["time"]
        # print("time is set to: ")
        # print(globAlarmHour)
        myAlarm.setTime(int(request.form["time"]))
        print("time is set to: ")
        print(myAlarm.getTime())
        return render_template("index.html", last_updated=dir_last_updated('static'), content=myAlarm.getTime())
    else:
        return render_template("index.html", last_updated=dir_last_updated('static'), content=myAlarm.getTime())

################################ TIME CHECKING ################################

# now = datetime.now()
#
# timestamp = datetime.timestamp(now)
# print("timestamp =", timestamp)

startTime = time.time()
interval = 20
global globAlarmHour
globAlarmHour = 8
# print("Seconds since epoch =", seconds)

def cleanAndExit(location):
    print("Cleaning... ", location)
    GPIO.cleanup()
    print("Bye!")
    sys.exit()

lock = threading.Lock()

def checkTime( threadName, interval):
    cumulativeInterval = 0
    timeZone = pytz.timezone("Europe/Amsterdam")
    timeAlarm = 0
    # timeAlarm = datetime.time(globAlarmHour, 0, tzinfo=timeZone)
    print("started thread")
    try:
        while True:
            val1 = hx1.get_weight(5)
            val2 = hx2.get_weight(5)
            val3 = hx3.get_weight(5)
            val4 = hx4.get_weight(5)
            print("Sensor 1: %.3f,\t 2: %.3f,\t 3: %.3f,\t 4: %.3f" % (val1, val2, val3, val4))
            # no weight:    -200~200
            # max weight:   10000

            hx1.power_down()
            hx1.power_up()
            hx2.power_down()
            hx2.power_up()
            hx3.power_down()
            hx3.power_up()
            hx4.power_down()
            hx4.power_up()
            # time.sleep(0.1)     # obsolete
            cumulativeInterval = cumulativeInterval + interval
            # print("Interval before if: \t", cumulativeInterval)

            # print( threadName, time.ctime(time.time()) )

            print(val1+val2+val3+val4)
            weightTotal = val1+val2+val3+val4

            # get time with % secons_in_day?
            # compare daily timestamps? lib?
            if weightTotal>1000:
                with lock:
                    timeAlarm = datetime.time(myAlarm.getTime(), 0, tzinfo=timeZone)
                currentTime = datetime.datetime.now(timeZone).time()
                # print("Interval in if: \t", cumulativeInterval)
                print("Current time: \t", currentTime)
                print("Alarm time: \t", timeAlarm)
                if currentTime <= timeAlarm:
                    print("Alarm go off")
                else:
                    print("Alarm no go off")

                # check if person on bed


            # print("Interval after if: \t", cumulativeInterval)
            time.sleep(interval)

    except (KeyboardInterrupt, SystemExit):
    	print('Bye :)')

    finally:
        cleanAndExit("Thread")

try:
    alarm = threading.Thread(target=checkTime, args=("alarmThread", 1,))
    alarm.start()
except:
   print("unable to start thread")


################################ MAIN LOOP ################################

if __name__ == "__main__":
    try:
        app.run(host= '0.0.0.0', debug=True, use_reloader=False)

        # elapsedTime = time.time()
        # if elapsedTime - startTime > interval:
        #     startTime = elapsedTime
        #     print("interval called")

    except (KeyboardInterrupt, SystemExit):
        print('Bye :)')

    finally:
    	# GPIO.cleanup()
        cleanAndExit("Main Loop")
