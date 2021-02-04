import os, bluetooth, subprocess, serial, time, threading, sys, datetime, pytz
from flask import Flask, redirect, url_for, render_template, request
import RPi.GPIO as GPIO

app = Flask(__name__)

################################ HX711 SETUP ################################

#   Manually import the local HX711 library since it's not installed via
#   site packages / pip.
sys.path.append('/home/pi/flask/hx711py')
from hx711 import HX711

#   Define 4 HX711 objects with respective pins for each load cell under the bed.
#   First parameter is for clock, second is for data. In the following code all 4
#   HX711s will be calibrated/setup to work.
hx1 = HX711(5, 6)
hx2 = HX711(20, 16)
hx3 = HX711(19, 13)
hx4 = HX711(22, 27)

#   Due to difference in versions for Python, the HX711 and numpy don't always communicate
#   data in a consistent way. The first parameter indicates how the bytes are odered
#   to build the long value, where the second parameter indicates the order of bits
#   in each byte.
hx1.set_reading_format("MSB", "MSB")
hx2.set_reading_format("MSB", "MSB")
hx3.set_reading_format("MSB", "MSB")
hx4.set_reading_format("MSB", "MSB")

#   Define a reference unit to transform values to a known weight. In a scale application
#   this is important to get values that match up the actual weights. With the iClock Air
#   knowing the correct weight is irrelevant, only a change in weight needs to occur.
hx1.set_reference_unit(2.959)
hx2.set_reference_unit(2.959)
hx3.set_reference_unit(2.959)
hx4.set_reference_unit(2.959)

#   Not sure why the HX711s need to be reset, but it seems to matter.
hx1.reset()
hx2.reset()
hx3.reset()
hx4.reset()

#   Tare each HX711 to set their readings back (read: close) to 0.
hx1.tare()
hx2.tare()
hx3.tare()
hx4.tare()

print("Tare done!")
#   HX711 ready for use

################################ ALARM OBJECT ################################

class Alarm:
  def __init__(self, alarmTime, alarmTime2):     # maybe (self, hours, minutes) ?
    self.alarmTime = alarmTime
    self.alarmTime2 = alarmTime2

  def setTime(self, alarmTime):
    self.alarmTime = alarmTime

  def setTime2(self, alarmTime2):
    self.alarmTime2 = alarmTime2

  def getTime(self):
    return self.alarmTime

  def getTime2(self):
    return self.alarmTime2

# p1 = Person("John", 36)
# p1.myfunc()

myAlarm = Alarm(18, 30)

################################ BT CONNECTION ################################

if os.path.exists('/dev/rfcomm0') == False:
    path = 'sudo rfcomm bind 0 98:D3:31:F5:9A:3C'
    os.system (path)
    time.sleep(1)
    # 00:21:13:00:44:23

if os.path.exists('/dev/rfcomm1') == False:
    path = 'sudo rfcomm bind 1 00:21:13:00:44:23'
    os.system (path)
    time.sleep(1)

# bluetoothSerial = serial.Serial( "/dev/rfcomm0", baudrate=9600 )
bluetoothSerial = serial.Serial( "/dev/rfcomm1", baudrate=9600 )
print("connnected to: \t", bluetoothSerial)

# count = 9
#
# j = str(count)
# b = j.encode()
# bluetoothSerial.write(b)
# print("sent: \t", b)

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
        myAlarm.setTime2(int(request.form["time2"]))
        print("time is set to: \t", myAlarm.getTime(), " hours")
        # print(myAlarm.getTime())
        print("and: \t\t\t", myAlarm.getTime2(), " minutes")
        return render_template("index.html", last_updated=dir_last_updated('static'), content=myAlarm.getTime(), content2=myAlarm.getTime2())
    else:
        return render_template("index.html", last_updated=dir_last_updated('static'), content=myAlarm.getTime(), content2=myAlarm.getTime2())

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
            # print("Sensor 1: %.3f,\t 2: %.3f,\t 3: %.3f,\t 4: %.3f" % (val1, val2, val3, val4))
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

            # print(val1+val2+val3+val4)
            weightTotal = val1+val2+val3+val4
            print("Total weight: \t", weightTotal)

            # get time with % secons_in_day?
            # compare daily timestamps? lib?
            if weightTotal>1500:
                with lock:
                    timeAlarm = datetime.time(myAlarm.getTime(), myAlarm.getTime2(), tzinfo=timeZone)
                    timeAlarmSnooze = datetime.time(myAlarm.getTime()+1, myAlarm.getTime2(), tzinfo=timeZone)
                currentTime = datetime.datetime.now(timeZone).time()
                # print("Interval in if: \t", cumulativeInterval)
                print("Current time: \t", currentTime)
                print("Alarm time: \t", timeAlarm)
                if currentTime >= timeAlarm and currentTime <= timeAlarmSnooze:
                    print("iClock Air go off.")
                    # bluetoothSerial.write(1)    # code number for arming
                    # bluetoothSerial.write(10)   # code number for small throttle
                    # bluetoothSerial.write(11)   # code number for high throttle
                    count = 7

                    j = str(count)
                    b = j.encode()
                    bluetoothSerial.write(b)
                    print("sent: \t", b)

                    time.sleep(4)

                    count2 = 1

                    i = str(count2)
                    c = i.encode()
                    bluetoothSerial.write(c)
                    bluetoothSerial.write(c)
                    print("sent: \t", c)

                    # count2 = 1
                    #
                    # i = str(count2)
                    # c = i.encode()
                    # bluetoothSerial.write(c)
                    # print("sent: \t", c)

                    time.sleep(5)

                    count3 = 6

                    k = str(count3)
                    d = k.encode()
                    bluetoothSerial.write(d)
                    print("sent: \t", d)

                    time.sleep(2)

                    count4 = 5

                    l = str(count4)
                    f = l.encode()
                    bluetoothSerial.write(f)
                    print("sent: \t", f)

                    count5 = 0

                    h = str(count5)
                    g = h.encode()
                    bluetoothSerial.write(g)
                    print("sent: \t", g)

                else:
                    print("iClock Air does nothing.")


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


    time.sleep(20)
    # count = 6
    #
    # j = str(count)
    # b = j.encode()
    # bluetoothSerial.write(b)
    # print("sent: \t", b)
    #
    # count2 = 7
    #
    # i = str(count2)
    # c = i.encode()
    # bluetoothSerial.write(c)
    # print("sent: \t", c)

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
