import requests
import random
import time
import json
import multiprocessing
from flask_cors import CORS
from flask import Flask
from multiprocessing import Process
import sys

app = Flask(__name__)
CORS(app)

CLIENTS = 10


@app.route('/start', methods=['get'])
def start():
    global process_pool
    print('Client starting')
    for _ in range(1, CLIENTS + 1):
        p = Process(target=send_request, args=(random.randint(1, _),))
        process_pool.append(p)
        p.start()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/stop', methods=['get'])
def stop():
    global process_pool
    print('Client shutting down...')
    for p in process_pool:
        print(f"stopping {str(p.pid)}")
        p.join()
        time.sleep(10)
        if p.is_alive():
            p.kill()
    print('Client stopped')
    sys.exit(0)


def send_request(id):
    while True:
        time.sleep(random.randint(0, 2))
        requests.get(f"http://0.0.0.0:8080/?clientid={id}")


if __name__ == '__main__':
    process_pool = []
    app.run(host="0.0.0.0", port=8080 + multiprocessing.cpu_count() + 1)
