from __future__ import print_function
import multiprocessing
import zmq


NBR_CLIENTS = 10
NBR_WORKERS = 3


def client_task(ident):
    socket = zmq.Context().socket(zmq.REQ)
    socket.identity = u"Client-{}".format(ident).encode("ascii")
    socket.connect("ipc://frontend.ipc")

    socket.send(b"HELLO")
    reply = socket.recv()
    print("{}: {}".format(socket.identity.decode("ascii"),
                          reply.decode("ascii")))


def worker_task(ident):
    socket = zmq.Context().socket(zmq.REQ)
    socket.identity = u"Worker-{}".format(ident).encode("ascii")
    socket.connect("ipc://backend.ipc")

    socket.send(b"READY")

    while True:
        address, empty, request = socket.recv_multipart()
        print("{}: {}".format(socket.identity.decode("ascii"),
                              request.decode("ascii")))
        socket.send_multipart([address, b"", b"OK"])


def main():
    context = zmq.Context.instance()
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("ipc://frontend.ipc")
    backend = context.socket(zmq.ROUTER)
    backend.bind("ipc://backend.ipc")

    def start(task, *args):
        process = multiprocessing.Process(target=task, args=args)
        process.daemon = True
        process.start()

    for i in range(NBR_CLIENTS):
        start(client_task, i)

    for i in range(NBR_WORKERS):
        start(worker_task, i)

    count = NBR_CLIENTS
    workers = []
    poller = zmq.Poller()
    poller.register(backend, zmq.POLLIN)

    while True:
        sockets = dict(poller.poll())

        if backend in sockets:
            request = backend.recv_multipart()
            worker, empty, client = request[:3]
            if not workers:
                poller.register(frontend, zmq.POLLIN)
            workers.append(worker)
            if client != b"READY" and len(request) > 3:
                empty, reply = request[3:]
                frontend.send_multipart([client, b"", reply])
                count -= 1
                if not count:
                    break

        if frontend in sockets:
            client, empty, request = frontend.recv_multipart()
            worker = workers.pop(0)
            backend.send_multipart([worker, b"", client, b"", request])
            if not workers:
                poller.unregister(frontend)

    backend.close()
    frontend.close()
    context.term()


if __name__ == '__main__':
    main()