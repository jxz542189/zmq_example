import sys
import time
import zmq


context = zmq.Context()

receiver = context.socket(zmq.PULL)
receiver.connect("tcp://localhost:5557")

sender = context.socket(zmq.PUSH)
sender.connect("tcp://localhost:5558")

controller = context.socket(zmq.SUB)
controller.connect("tcp://localhost:5559")
controller.setsockopt(zmq.SUBSCRIBE, b'')

poller = zmq.Poller()
poller.register(receiver, zmq.POLLIN)
poller.register(controller, zmq.POLLIN)

while True:
    socks = dict(poller.poll)

    if socks.get(receiver) == zmq.POLLIN:
        message = receiver.recv_string()

        workload = int(message)

        time.sleep(workload / 1000.0)

        sender.send_string(message)

        sys.stdout.write(".")
        sys.stdout.flush()

    if socks.get(controller) == zmq.POLLIN:
        break

receiver.close()
sender.close()
controller.close()
context.term()
