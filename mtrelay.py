import threading
import zmq


def step1(context=None):
    context = context or zmq.Context.instance()
    sender = context.socket(zmq.PAIR)
    sender.connect("inproc://step2")

    sender.send(b"")


def step2(context=None):
    context = context or zmq.Context.instance()
    receiver = context.socket(zmq.PAIR)
    receiver.bind("inproc://step2")

    thread = threading.Thread(target=step1)
    thread.start()

    msg = receiver.recv()

    sender = context.socket(zmq.PAIR)
    sender.connect("inproc://step3")
    sender.send(b"")


def main():
    context = zmq.Context.instance()

    receiver = context.socket(zmq.PAIR)
    receiver.bind("inproc://step3")

    thread = threading.Thread(target=step2)
    thread.start()

    string = receiver.recv()
    print("Test successful!")

    receiver.close()
    context.term()


if __name__ == '__main__':
    main()