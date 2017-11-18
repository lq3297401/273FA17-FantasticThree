'''
################################## client.py #############################
# 
################################## client.py #############################
'''
import random
import time
import grpc
import datastore_pb2
import datastore_pb2_grpc
import argparse
import uuid
import rocksdb

PORT = 3000

'''
Request Generator
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
    for task in tasks:
        print("Sending key %s and data %s" % (task.key, task.data))
        yield task
        time.sleep(random.uniform(0.5, 1.0))

class DatastoreClient():
    
    def __init__(self, host='0.0.0.0', port=PORT):
        self.channel = grpc.insecure_channel('%s:%d' % (host, port))
        self.stub = datastore_pb2.DatastoreStub(self.channel)
        self.db = rocksdb.DB("hw2_follower.db", rocksdb.Options(create_if_missing=True))

    '''
    Bidirectional streaming RPC
    Client send streaming data for server to take action.
    '''

    def put(self):
        resps = self.stub.put(generate_request())
        if resps == None:
            print("Empty!")
        else:
            for resp in resps:
                print("Master stored key %s and value %s" % (resp.key, resp.data))

    def delete(self):
        resps = self.stub.delete(generate_request())
        if resps == None:
            print("Empty!")
        else:
            for resp in resps:
                print("Master deleted key %s and value %s" % (resp.key, resp.data))

    '''
    A server-to-client streaming RPC
    Master send sterming data for follower to replicate
    '''

    def replicator(self, action):
        resp = self.stub.replicator(datastore_pb2.PullRequest(action=action))
        if action == 'put':
            for action in resp:
                self.db.put(action.key.encode(), action.data.encode())
                if action.data == self.db.get(action.key.encode()).decode():
                    print("Follower stored key %s and value %s" % (action.key, action.data))
        elif action == 'delete':
            for action in resp:
                self.db.delete(action.key.encode())
                if self.db.get(action.key.encode()) == None:
                    print("Follower deleted key %s and value %s" % (action.key, action.data))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="display a square of a given number")
    args = parser.parse_args()
    print("Client is connecting to Server at {}:{}...".format(args.host, PORT))
    client = DatastoreClient(host=args.host)
    
    '''
    Test Case
    '''
    client.put()
    client.replicator("put")
    client.delete()
    client.replicator("delete")

if __name__ == "__main__":
    main()