import threading
import zmq


def step1(context=None):
    context = context or zmq.Context.instance()
    sender = context.socket(zmq.PAIR)
    sender.connect