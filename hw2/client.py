'''
################################## client.py #############################
# 
################################## client.py #############################
'''
import random
import time
import grpc
import datastore_pb2
import argparse
import uuid
import rocksdb

PORT = 3000

'''
Input Data
'''

def make_data(key, data):
  return datastore_pb2.Request(
      key=key,
      data=data)

def generate_request():
    tasks = [
            make_data('100', 'Forrest'),
            make_data('101', 'Chen'),
            make_data('102', 'is'),
            make_data('103', 'a'),
            make_data('104', 'student'),       
    ]
    for piece in tasks:
        print("Sending key %s and data %s" % (piece.key, piece.data))
        yield piece
        time.sleep(random.uniform(0.5, 1.0))

class DatastoreClient():
    
    def __init__(self, host='0.0.0.0', port=PORT):
        self.channel = grpc.insecure_channel('%s:%d' % (host, port))
        self.stub = datastore_pb2.DatastoreStub(self.channel)
        self.db = rocksdb.DB("hw2_follower.db", rocksdb.Options(create_if_missing=True))
    
    def put(self):
        resps = self.stub.put(generate_request())
        for resp in resps:
            print("Master stored key %s and value %s" % (resp.key, resp.data))
            self.db.put(resp.key.encode(), resp.data.encode())
            if resp.data == self.db.get(resp.key.encode()).decode():
                print("Follower stored key %s and value %s" % (resp.key, resp.data))

    def delete(self):
        resps = self.stub.put(generate_request())
        for resp in resps:
            print("Master deleted key %s and value %s" % (resp.key, resp.data))
            self.db.delete(resp.key.encode())
            if self.db.get(resp.key.encode()) == None:
                print("Follower deleted key %s and value %s" % (resp.key, resp.data))

    # def put_replicator(some_function):

    #     def wrapper(self, arg):
    #         mykey = some_function(arg)
    #         print("Start here")
    #         self.db.put(mykey.encode(), arg.encode())
    #         myvalue = self.db.get(mykey.encode()).decode()
    #         print("## Copy key = " + mykey)
    #         print("## Copy value = " + myvalue)
    #         print("End here")
    #         return mykey
    #     return wrapper

    # def delete_replicator(some_function):

    #     def wrapper(arg):
    #         print("## Delete key =" + arg)
    #         self.db.delete(arg.encode())
    #         checkvalue = db.get(arg.encode())
    #         if checkvalue == None:
    #             print("Good!")
    #         else:
    #             print("Bad!")
    #     return wrapper

    # @put_replicator
    # def test_put(value):
    #     print("## PUT Request: value = " + value) 
    #     resp = self.stub.put(value)
    #     print("## PUT Response: key = " + resp.data)
    #     return resp.data

    # @delete_replicator
    # def delete(key):
    #     pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="display a square of a given number")
    args = parser.parse_args()
    print("Client is connecting to Server at {}:{}...".format(args.host, PORT))
    client = DatastoreClient(host=args.host)
    
    client.put()
    client.delete()

if __name__ == "__main__":
    main()