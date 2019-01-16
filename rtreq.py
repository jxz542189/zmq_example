import time
import random
from threading import Thread

import zmq
import zhelpers


NEB_WORKERS = 10


def worker_thread(context=None):
    context = context or zmq.Context.instance()
    worker = context.socket(zmq.REQ)

    zhelpers.set_id(worker)
    worker.connect("tcp://localhost:5671")

    total = 0
    while True:
        worker.send(b"ready")

        workload = worker.recv()
        finished = workload == b"END"
        if finished:
            print("Processed: %d tasks" % total)
            break
        total += 1

        time.sleep(0.1 * random.random())

context = zmq.Context.instance()
client = context.socket(zmq.ROUTER)
client.bind("tcp://*:5671")

for _ in range(NEB_WORKERS):
    Thread(target=worker_thread).start()

for _ in range(NEB_WORKERS * 1000):
    address, empty, ready = client.recv_multipart()

    client.send_multipart([
        address,
        b'',
        b'This is the workload'
    ])

for _ in range(NEB_WORKERS):
    address, empty, ready = client.recv_multipart()
    client.send_multipart([
        address,
        b'',
        b'END',
    ])