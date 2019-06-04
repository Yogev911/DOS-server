import json
import time
import datetime
from flask_cors import CORS
from flask import Flask, request

app = Flask(__name__)
CORS(app)

TIME_FRAME = 5
MAX_CONNECTIONS = 5

shared_dict = None
lock = None


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...', 200


@app.route("/connection", methods=['GET'])
def calc_connection():
    client_id = request.args.get('clientid')
    input_time = time.mktime(datetime.datetime.today().timetuple())
    end_time = input_time + TIME_FRAME
    lock.acquire()
    if client_id not in shared_dict:
        shared_dict[client_id] = [end_time, 1]
        print(f"client: {client_id} active conn 1")
        res = json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        res = handel_existing_client(client_id, end_time, input_time)
    lock.release()
    return res


def handel_existing_client(client_id, end_time, input_time):
    global shared_dict
    frame_end_time = shared_dict[client_id][0]
    active_connection = shared_dict[client_id][1]
    delta_time = frame_end_time - input_time
    if active_connection < MAX_CONNECTIONS and delta_time >= 0:
        shared_dict[client_id][1] += 1
        res = json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        print(f"client: {client_id} active conn {active_connection + 1}, delta time {delta_time}")

    elif delta_time < 0:
        # new frame
        shared_dict[client_id] = [end_time, 1]
        res = json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        print(f"client: {client_id} active conn 1, opened new frame")

    elif active_connection == MAX_CONNECTIONS and delta_time >= 0:
        # dismiss connections
        res = json.dumps({'success': False}), 503, {'ContentType': 'application/json'}
        print(f"client: {client_id} active conn {active_connection}, dropped request")

    else:
        print(f"client: {client_id}")
        res = json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
    return res


def worker(data):
    global shared_dict, lock
    shared_dict = data['dict']
    lock = data['lock']
    app.run(host="0.0.0.0", port=data['port'])
