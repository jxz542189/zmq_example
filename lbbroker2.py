from __future__ import print_function
import threading
import time
import zmq

NBR_CLIENTS = 10
NBR_WORKERS = 3


def worker_thread(worker_url, context, i):
    socket = context.socket(zmq.REQ)

    socket.identity = (u"Worker-%d" % i).encode('ascii')
    socket.connect(worker_url)

    socket.send(b"READY")

    try:
        while True:
            address, empty, request = socket.recv_multipart()
            print("%s: %s\n" % (socket.identity.decode('ascii'),
                                request.decode('ascii')), end='')
            socket.send_multipart([address, b'', b'OK'])
    except zmq.ContextTerminated:
        return


def client_thread(client_url, context, i):
    socket = context.socket(zmq.REQ)
    socket.identity = (u"Client-%d" % i).encode('ascii')

    socket.connect(client_url)

    socket.send(b"HELLO")
    reply = socket.recv()

    print("%s: %s\n" % (socket.identity.decode('ascii'),
                        reply.decode('ascii')), end='')


def main():
    url_worker = "inproc://workers"
    url_client = "inproc://clients"
    client_nbr = NBR_CLIENTS

    context = zmq.Context()
    frontend = context.socket(zmq.ROUTER)
    frontend.bind(url_client)
    backend = context.socket(zmq.ROUTER)
    backend.bind(url_worker)

    for i in range(NBR_WORKERS):
        thread = threading.Thread(target=worker_thread,
                                  args=(url_worker, context, i,))
        thread.start()

    for i in range(NBR_CLIENTS):
        thread_c = threading.Thread(target=client_thread,
                                    args=(url_client, context, i,))
        thread_c.start()

    available_workers = 0
    workers_list = []

    poller = zmq.Poller()

    poller.register(backend, zmq.POLLIN)

    poller.register(frontend, zmq.POLLIN)

    while True:
        socks = dict(poller.poll())

        if (backend in socks and socks[backend] == zmq.POLLIN):
            message = backend.recv_multipart()
            assert available_workers < NBR_WORKERS

            worker_addr = message[0]

            available_workers += 1
            workers_list.append(worker_addr)

            empty = message[1]
            assert empty == b""

            client_addr = message[2]

            if client_addr != b"READY":
                empty = message[3]
                assert empty == b""

                reply = message[4]

                frontend.send_multipart([client_addr, b"", reply])

                client_nbr -= 1

                if client_nbr == 0:
                    break

        if available_workers > 0:
            if (frontend in socks and socks[frontend] == zmq.POLLIN):
                [client_addr, empty, request] = frontend.recv_multipart()

                assert empty == b""
                available_workers += -1
                worker_id = workers_list.pop()

                backend.send_multipart([worker_id, b"",
                                        client_addr, b"", request])

    time.sleep(1)
    frontend.close()
    backend.close()
    context.term()


if __name__ == '__main__':
    main()