#!flask/bin/python

import threading
import time

from flask import Flask
from flask import request

import RPi.GPIO as IO

app = Flask(__name__)

timeVar = "HH:mm"
ranScript = False


@app.route("/")
def index():
    return timeVar


@app.route("/", methods=['POST'])
def update_time():
    if request.json and "time" in request.json:
        global timeVar
        timeVar = request.json["time"]
        print timeVar
    return timeVar


@app.route("/", methods=["DELETE"])
def stop_coffee():
    global timeVar
    timeVar = "OFF"


def check_alarms():
    current_time = time.strftime("%H:%M", time.localtime())
    global ranScript
    if current_time == timeVar and ranScript == False:
        ranScript = True
        print "It is " + timeVar + ":\tTime for coffee"
        IO.setmode(IO.BCM)
        IO.setup(17, IO.OUT)
        IO.output(17, 1)
        time.sleep(36)
        IO.output(17, 0)
        IO.cleanup()
    elif current_time != timeVar and ranScript == True:
        ranScript = False
    timer = threading.Timer(1.0, check_alarms)
    timer.setDaemon(True)
    timer.start()


check_alarms()

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
