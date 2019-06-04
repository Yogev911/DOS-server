import signal
from multiprocessing import Pool, Manager, cpu_count, Process

import requests

import LoadBalancer
import server

CPUS = cpu_count()
if __name__ == '__main__':
    try:
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = Pool(processes=CPUS)
        lb = Process(target=LoadBalancer.worker, args=(8080,))
        lb.start()
        signal.signal(signal.SIGINT, original_sigint_handler)
        manager = Manager()
        input_list = [{"dict": {}, "lock": manager.Lock(), "port": i} for i in range(8081, 8081 + CPUS)]

        pool.map(server.worker, input_list)
    except (KeyboardInterrupt, SystemExit):
        print("Caught KeyboardInterrupt, terminating workers")
        for port in range(8080 + CPUS, 8079, -1):
            print(f"http://localhost:{port}/shutdown")
            requests.post(f"http://localhost:{port}/shutdown")
        pool.close()
        pool.join()
        pool.terminate()
        print('killing lb')
        lb.join(60)
        if lb.is_alive():
            lb.kill()
        print("lb is down")
