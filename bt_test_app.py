import os, bluetooth, subprocess, serial, time
from flask import Flask, redirect, url_for, render_template, request

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

# @app.route("/alarm", methods=["POST", "GET"])
# def submitTime():
#     return render_template("index.html")

@app.route("/", methods=["POST", "GET"])
def home():
    print("went to home")
    if request.method == "POST":
        alarmTime = request.form["time"]
        print("time is set to: ")
        print(alarmTime)
        return render_template("index.html", last_updated=dir_last_updated('static'), content=alarmTime)
    else:
        return render_template("index.html", last_updated=dir_last_updated('static'))

if __name__ == "__main__":
        app.run(host= '0.0.0.0', debug=True)
