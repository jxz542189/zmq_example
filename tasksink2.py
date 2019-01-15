import sys
import time
import zmq


context = zmq.Context()

receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5558")

controller = context.socket(zmq.PUB)
controller.bind("tcp://*:5559")

receiver.recv()

tstart = time.time()

for task_nbr in range(100):
    receiver.recv()
    if task_nbr % 10 == 0:
        sys.stdout.write(":")
    else:
        sys.stdout.write(".")
    sys.stdout.flush()


tend = time.time()
tdiff = tend - tstart
total_msec = tdiff * 1000
print("Total elapsed time: %d msec" % total_msec)

controller.send(b"KILL")
receiver.close()
controller.close()
context.term()