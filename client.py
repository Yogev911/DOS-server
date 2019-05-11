import requests
import random
import multiprocessing
from flask_cors import CORS
from flask import Flask
from multiprocessing import Pool
import traceback
app = Flask(__name__)
CORS(app)

CLIENTS = 20
CPUS = multiprocessing.cpu_count()


def send_request(id):
    try:
        print(f"{id} ", end='')
        while True:
            res = requests.get(f"http://localhost:8080/?clientid={id}")
            if res.status_code == 503:
                print(f"request dropped on id {id}")
            elif res.status_code != 200:
                print(f"{res.status_code}")
    except requests.exceptions.ConnectionError:
        print("server is down")
    except Exception as e:
        print(traceback.format_exc())


if __name__ == '__main__':
    try:
        input_list = [random.randint(1, CLIENTS) for i in range(1, CLIENTS + 1)]
        with Pool(processes=CPUS) as pool:
            pool.map(send_request, input_list)
    except KeyboardInterrupt:
        pool.close()
        pool.join()
