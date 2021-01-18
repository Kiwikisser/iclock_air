import os, bluetooth, subprocess
from flask import Flask, redirect, url_for, render_template

nearby_devices = bluetooth.discover_devices(duration=4, lookup_names=True, flush_cache=True, lookup_class=False)

name = "HC05"      # Device name
addr = "98:D3:31:F5:9A:3C"      # Device Address
port = 1         # RFCOMM port
passkey = "1234" # passkey of the device you want to connect

# kill any "bluetooth-agent" process that is already running
# subprocess.call("sudo kill -9 500",shell=True)

# Start a new "bluetooth-agent" process where XXXX is the passkey
# status = subprocess.call("bluetooth-agent " + passkey + " &",shell=True)

# Now, connect in the same way as always with PyBlueZ
try:
    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.connect((addr,port))
    s.send("1")
    s.send("2")
    s.send("3")
    s.send("4")
except bluetooth.btcommon.BluetoothError as err:
    print(err)
    pass

app = Flask(__name__)

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

@app.route("/")
def home():
    return render_template("index.html", last_updated=dir_last_updated('static'))

if __name__ == "__main__":
        app.run(host= '0.0.0.0', debug=True)
