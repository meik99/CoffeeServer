#!flask/bin/python

import threading
import time
import json
import re

from flask import Flask
from flask import request

import RPi.GPIO as IO

app = Flask(__name__)

CODE_TIME_SET = 0
CODE_ERROR_PATTERN = 1

MESSAGE_TIME_SET = "TIME SET"
MESSAGE_ERROR_PATTERN = "TIME COULD NOT BE PARSED"

time_set = 0
make_coffee = False


@app.route("/time", methods=["GET"])
def get_time():
    return json.dumps({"time": time_set, "on": make_coffee})


@app.route("/time", methods=["POST"])
def set_time():
    pattern = re.compile("[0-9]{1,2}:[0-9]{2}")

    if (request.json and
            "time" in request.json):
        request.json.time = str(request.json.time)

        if pattern.match(request.json.time) is not None:
            if len(request.json.time) is 4:
                request.json.time = "0" + request.json.time

            global time_set
            time_set = time.strptime(request.json.time, "%H:%M")
            return json.dumps({"code": CODE_TIME_SET, "message": MESSAGE_TIME_SET})
        else:
            return json.dumps({"code": CODE_ERROR_PATTERN, "message": MESSAGE_ERROR_PATTERN})
    else:
        return json.dumps({"code": CODE_ERROR_PATTERN, "message": MESSAGE_ERROR_PATTERN})


@app.route("/time/stop", methods=["GET"])
def stop_coffee():
    global make_coffee
    make_coffee = False
    return get_time()


@app.route("/time/start", methods=["GET"])
def start_coffee():
    global make_coffee
    make_coffee = True
    return get_time()
#
#
# @app.route("/")
# def index():
#     return timeVar
#
#
# @app.route("/", methods=['POST'])
# def update_time():
#     if request.json and "time" in request.json:
#         global timeVar
#         timeVar = request.json["time"]
#         print timeVar
#     return timeVar
#
#
# @app.route("/", methods=["DELETE"])
# def stop_coffee():
#     global timeVar
#     timeVar = "OFF"
#     return timeVar


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
