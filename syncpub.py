import zmq


SUBSCRIBERS_EXPECTED = 10


def main():
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.sndhwm = 1100000
    publisher.bind("tcp://*:5561")

    syncservice = context.socket(zmq.REP)
    syncservice.bind("tcp://*:5562")

    subscribers = 0
    while subscribers < SUBSCRIBERS_EXPECTED:
        msg = syncservice.recv()
        syncservice.send(b'')
        subscribers += 1
        print("+1 subscriber (%i/%i)" % (subscribers, SUBSCRIBERS_EXPECTED))

    for i in range(1000000):
        publisher.send(b"Rhubarb")

    publisher.send(b'END')


if __name__ == '__main__':
    main()