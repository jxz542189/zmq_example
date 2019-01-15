import time
import threading
import zmq


def worker_routine(worker_url, context=None):
    context = context or zmq.Context.instance()
    socket = context.socket(zmq.REP)

    socket.connect(worker_url)

    while True:
        string = socket.recv()

        print("Received request: [ %s ]" % (string))

        time.sleep(1)

        socket.send(b"World")


def main():
    url_worker = "inproc://workers"
    url_client = "tcp://*:5555"

    context = zmq.Context.instance()
    clients = context.socket(zmq.ROUTER)
    clients.bind(url_client)

    workers = context.socket(zmq.DEALER)
    workers.bind(url_worker)

    for i in range(5):
        thread = threading.Thread(target=worker_routine,
                                  args=(url_worker,))
        thread.start()

    zmq.proxy(clients, workers)

    clients.close()
    workers.close()
    context.term()


if __name__ == '__main__':
    main()
