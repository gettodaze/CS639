import os
import pickle
import time
import socket
import signal
import codec

import builtins
import io

class RestrictedUnpickler(pickle.Unpickler):
    """"This class will restrict the unpickler from using any unpickling method except for
    codec.myDecode. Raises an Unpickling Error upon discovery of the attempt to use a
    different unpickling method."""
    def find_class(self, module, name):
        # Only allow safe classes from builtins.
        print(module)
        if module == "codec" and name == 'myDecode':
            return getattr(codec, name)
        # Forbid everything else.
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" %
                                     (module, name))

def restricted_loads(s):
    """Helper function analogous to pickle.loads().
    This method creates a RestrictedUnpickler to load data
    from the more secure"""
    return RestrictedUnpickler(io.BytesIO(s)).load()

# function to get data from client, deserialize it, and print it
def server(soc):
    # get the raw data from the client connection
    payload = soc.recv(1024)
    # deserialize the data to an object (expecting string encoded by our codec.py)
    # message = pickle.loads(payload)
    try:
        #Attempt to open the payload and catch any unpickling error
        # that may occur in the process
        message = restricted_loads(payload)
        print "Server Received: %s" % message
    # print the string we received
    except pickle.UnpicklingError as e:
        print "Unpickling error! {0}".format(e)
    

    # print the string we received
    print "Server Received: %s" % message


print "------------------Server Starting------------------"

# bind server on local address
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
soc.bind (("localhost", 10014))
soc.listen(10)

# loop infinitely to handle all incoming connections
while True:
    # wait for client connection
    clientSoc, addr = soc.accept()
    print "A connection from %s:%d is here" % (addr[0], addr[1])

    # handle in new thread
    if (os.fork() == 0):
        # send acceptance message to client
        clientSoc.send("Accepted connection from  %s:%d" % (addr[0], addr[1]))
        # receive and handle data from client
        server(clientSoc)
        # exit the handling thread
        exit(0)

print "--------------------Server Exit--------------------"
soc.close()
