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

#   Not sure why the HX711s need to be reset(), but it seems to matter.
#   Maybe to flush the registers to set up following tare.
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
#   HX711 ready for use, readings get handled in alarm thread.

################################ ALARM OBJECT ################################

#   Define Alarm object with hour and minute parameters. Values stored in an object
#   can be retrieved and interacted with in functions, in contrary to basic values.
#   Hours and minutes values get getters and setters each, for changing and retrieving.
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

#   Instantiate initial alarm object with example/default timestamp.
hours = 18
minutes = 30
myAlarm = Alarm(hours, minutes)

################################ BT CONNECTION ################################

#   Bind the radio frequency communication device to the Pi with address of external device.
#   HC05 address can be scanned with use of hcitool scan.
#   If system is rebooted, the path needs needs to be re-added. Path gets added through
#   execution of root command.
if os.path.exists('/dev/rfcomm0') == False:
    path = 'sudo rfcomm bind 0 98:D3:31:F5:9A:3C'
    os.system (path)
    time.sleep(1)

#   Idem dito for other test HC05 module
if os.path.exists('/dev/rfcomm1') == False:
    path = 'sudo rfcomm bind 1 00:21:13:00:44:23'
    os.system (path)
    time.sleep(1)

#   Instantiate serial connection object
# bluetoothSerial = serial.Serial( "/dev/rfcomm0", baudrate=9600 )
bluetoothSerial = serial.Serial( "/dev/rfcomm1", baudrate=9600 )

################################ CACHE FIX ################################

#   In order for flask to recognise changes in files, a timestamp from latest modified file
#   from folder in paramter is retrieved to later pass to front end and fix cache not updating.
def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

################################ WEB ROUTES ################################

#   Route for the webpage. URL is specified in function decorator, followed by allowed HTTP
#   requests. By default the index.html will be loaded (GET request), with the timestamp of latest
#   modified file, and alarm hours and minutes. If the HTTP request is POST, then alarm times
#   get retrieved from submitted form, stored into alarm object and passed back to index.html again.
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        myAlarm.setTime(int(request.form["time"]))
        myAlarm.setTime2(int(request.form["time2"]))
        print("time is set to: \t", myAlarm.getTime(), " hours")
        print("and: \t\t\t", myAlarm.getTime2(), " minutes")
        return render_template("index.html", last_updated=dir_last_updated('static'), content=myAlarm.getTime(), content2=myAlarm.getTime2())
    else:
        return render_template("index.html", last_updated=dir_last_updated('static'), content=myAlarm.getTime(), content2=myAlarm.getTime2())

################################ GPIO CLEANING ################################

#   Always clean your IO pins at the end of your script. In this case it gets called on every
#   script exit or crash in general.
def cleanAndExit(location):
    print("Cleaning... ", location)
    GPIO.cleanup()
    print("Bye!")
    sys.exit()

################################ TIME CHECKING ################################

#   Instantiate lock for thread. The lock is used to access the Alarm object outside thread.
lock = threading.Lock()

#   Function that will be used for the thread, name is passed as parameter for convinience.
#   To summarise, based on the values given by the loadcells/HX711s under the bed it will check
#   if a person is sitting on a bed based on difference in total measured value from previous
#   iteration of the loop. If the conditions are met, the current time will be compared to to the
#   set alarm time and will then "go off", up to an hour after the alarm time (snooze).
def checkTime( threadName):
    #   To retrieve the current time in a hh:mm:ss format, a timezone will be instantiated.
    #   Furthermore at the start of the function we instantiate variables with basic values,
    #   with a relatively high number for previousWeight so the alarm won't get triggered on
    #   first iterations of the loop. Threshold should be high enough so alarm won't be triggered
    #   by bumps etc. but low enough to register a person getting onto the bed.\
    timeZone = pytz.timezone("Europe/Amsterdam")
    # timeAlarm = 0
    snoozeTime = 1
    previousWeight = 100000
    threshold = 2000
    print("started thread")

    #   Put while True loop in try catch block to account for inevitable crashes.
    try:
        while True:

            #   Retrieve weigh reading from all HX711s. The "5" as parameter serves for times
            #   measured before an average value is normalised and returned. Any value other than 5
            #   seems to crash the script due to int float type mismatch in division.
            val1 = hx1.get_weight(5)
            val2 = hx2.get_weight(5)
            val3 = hx3.get_weight(5)
            val4 = hx4.get_weight(5)

            weightTotal = val1+val2+val3+val4
            print("Total weight: \t", weightTotal)

            #   Compared previous measured weight with new weight. Enter if-statement if increase
            #   in weight exceeds the threshold. Assign weight total to previousWeight var in else.
            #   After entering if-statement, retrieve time and snoozeTime in with-lock-statement and
            #   subsequently compare with currentTime.
            # TODO: set default threshold of person on bed.
            if weightTotal>previousWeight+threshold:
                with lock:
                    timeAlarm = datetime.time(myAlarm.getTime(), myAlarm.getTime2(), tzinfo=timeZone)
                    timeAlarmSnooze = datetime.time(myAlarm.getTime()+snoozeTime, myAlarm.getTime2(), tzinfo=timeZone)
                currentTime = datetime.datetime.now(timeZone).time()
                print("Current time: \t", currentTime)
                print("Alarm time: \t", timeAlarm)

                #   Alarm goes off if currentTime is between set alarm time and snoozeTime, bluetooth
                #   codes will be sent to the drone to disarm, rearm, set throttle low and set throttle
                #   high. Codes must be turned into strings and encoded to be sent through the BTserial.
                #   Sleeps between each message to give the Nano on the drone time compute before
                #   receiving nect code.
                if currentTime >= timeAlarm and currentTime <= timeAlarmSnooze:
                    print("iClock Air go off.")

                    count0 = 0

                    u = str(count0)
                    p = u.encode()
                    bluetoothSerial.write(p)
                    print("sent: \t", p)

                    time.sleep(1)

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

                    time.sleep(5)

                    count3 = 6

                    k = str(count3)
                    d = k.encode()
                    bluetoothSerial.write(d)
                    print("sent: \t", d)

                    time.sleep(15)

                else:
                    print("iClock Air does nothing.")

            else:
                previousWeight = weightTotal

    except (KeyboardInterrupt, SystemExit):
    	print('Bye :)')

    finally:
        cleanAndExit("Thread")

#   Instantiate the thread with above checkTime function in try catch statement.
try:
    alarm = threading.Thread(target=checkTime, args=("alarmThread", ))
    alarm.start()
except:
   print("unable to start thread")


################################ MAIN LOOP ################################

#   Finally start Flask app in try catch statement. IO pins will always be cleaned up
#   regardless of app or thread crashing.
if __name__ == "__main__":
    try:
        app.run(host= '0.0.0.0', debug=True, use_reloader=False)

    except (KeyboardInterrupt, SystemExit):
        print('Bye :)')

    finally:
        cleanAndExit("Main Loop")
