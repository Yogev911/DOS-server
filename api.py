import sys
import json
import time
import datetime
import multiprocessing
from flask_cors import CORS
from flask import Flask, request, redirect
from multiprocessing import Process, Lock

app = Flask(__name__)
CORS(app)

TIME_FRAME = 5
MAX_CONNECTIONS = 5
CPUS = multiprocessing.cpu_count()


@app.route('/stop', methods=['get'])
def stop():
    global process_pool
    print('Server shutting down...')
    for p in process_pool:
        print(f"stopping {str(p.pid)}")
        p.join()
        time.sleep(10)
        if p.is_alive():
            p.kill()
    print('Server stopped')
    sys.exit(0)


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


@app.route("/", methods=['GET'])
def root():
    global shared_dict, lock
    client_id = int(request.args.get('clientid'))
    print(f"http://0.0.0.0:{str((client_id % CPUS) + 8080)}/connection?clientid=3")
    return redirect(f"http://0.0.0.0:{str((client_id % CPUS) + 8080)}/connection?clientid=3", code=302)


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
        print(f"client: {client_id} active conn {1}, opened new frame")

    elif active_connection == MAX_CONNECTIONS and delta_time >= 0:
        # dismiss connections
        res = json.dumps({'success': False}), 503, {'ContentType': 'application/json'}
        print(f"client: {client_id} active conn {active_connection}, dropped request")

    else:
        print(f"client: {client_id}")
        res = json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
    return res


if __name__ == '__main__':
    shared_dict = {}
    process_pool = []
    lock = Lock()
    for _ in range(1, CPUS + 1):
        p = Process(target=app.run, args=("0.0.0.0", 8080 + _,))
        process_pool.append(p)
        p.start()
    app.run(host="0.0.0.0", port=8080)
