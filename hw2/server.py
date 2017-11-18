'''
################################## server.py #############################
# Lab1 gRPC RocksDB Server 
################################## server.py #############################
'''
import random
import time
import grpc
import datastore_pb2
import datastore_pb2_grpc
import uuid
import rocksdb

from concurrent import futures

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

'''
Container
'''
put_tasks = []
delete_tasks = []

'''
Replicator decorator
'''

def my_replicator(some_function):
    def wrapper(*args, **kwargs):
        if args[1].action == 'put':
            print("Get pull request from follower (put)")
            print("*************************************")
            for task in put_tasks:
                print("Pushing key %s and data %s" % (task.key, task.data))
                yield task
                time.sleep(random.uniform(0.5, 1.0))
            print("Completed (put)")
            print("***************")
            put_tasks.clear()

        elif args[1].action == 'delete':
            print("Get pull request from follower (delete)")
            print("***************************************")
            for task in delete_tasks:
                print("Pushing key %s and data %s" % (task.key, task.data))
                yield task
                time.sleep(random.uniform(0.5, 1.0))
            print("Completed (delete)")
            print("******************")
            delete_tasks.clear()

        return some_function(*args, **kwargs)
    return wrapper

class MyDatastoreServicer(datastore_pb2.DatastoreServicer):
    def __init__(self):
        self.db = rocksdb.DB("hw2_master.db", rocksdb.Options(create_if_missing=True))

    def put(self, request_iterator, context):
        for new_task in request_iterator:
            self.db.put(new_task.key.encode(), new_task.data.encode())
            if new_task.data == self.db.get(new_task.key.encode()).decode():
                put_tasks.append(new_task)
            yield datastore_pb2.Response(key=new_task.key, data=new_task.data)

    def delete(self, request_iterator, context):
        for new_task in request_iterator:
            self.db.delete(new_task.key.encode())
            if self.db.get(new_task.key.encode()) == None:
                delete_tasks.append(new_task)
            yield datastore_pb2.Response(key=new_task.key, data=new_task.data)

    @my_replicator
    def replicator(self, request, context):
        pass

def run(host, port):
    '''
    Run the GRPC server
    '''
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    datastore_pb2_grpc.add_DatastoreServicer_to_server(
        MyDatastoreServicer(), server)
    server.add_insecure_port('%s:%d' % (host, port))
    server.start()

    try:
        while True:
            print("Server started at...%d" % port)
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    run('0.0.0.0', 3000)