from multiprocessing import Pool, Manager, cpu_count, Process
import LoadBalancer
import server

CPUS = cpu_count()
if __name__ == '__main__':
    try:
        lb = Process(target=LoadBalancer.worker, args=(8080,))
        manager = Manager()
        lb.start()
        input_list = [{"dict": {}, "lock": manager.Lock(), "port": 8080 + i} for i in range(1, CPUS + 1)]
        with Pool(processes=CPUS) as pool:
            pool.map(server.worker, input_list)
    except KeyboardInterrupt:
        lb.join(60)
        if lb.is_alive():
            lb.kill()
        pool.close()
        pool.join()
