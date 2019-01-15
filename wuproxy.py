import zmq


context = zmq.Context()
frontend = context.socket(zmq.SUB)
frontend.connect("tcp://192.168.55.210:5556")

backend = context.socket(zmq.PUB)
backend.bind("tcp://10.1.1.0:8100")

frontend.setsockopt(zmq.SUBSCRIBE, b'')

while True:
    message = frontend.recv_multipart()
    backend.send_multipart(message)