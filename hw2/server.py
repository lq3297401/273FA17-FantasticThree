'''
################################## server.py #############################
# Lab1 gRPC RocksDB Server 
################################## server.py #############################
'''
import time
import grpc
import datastore_pb2
import datastore_pb2_grpc
import uuid
import rocksdb

from concurrent import futures

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

put_tasks = []
delete_tasks = []

class MyDatastoreServicer(datastore_pb2.DatastoreServicer):
    def __init__(self):
        self.db = rocksdb.DB("hw2_master.db", rocksdb.Options(create_if_missing=True))

    def put_replicator(some_function):
        def wrapper(*args, **kwargs):
            for new_task in request_iterator:
                for prev_task in prev_tasks:
                    print("Wrapper get" + new_task.key + " " + new_task.data)
                    yield prev_task
                prev_tasks.append(new_task)
            some_function(*args, **kwargs) 
        return wrapper

    # @put_replicator
    def put(self, request_iterator, context):
        for new_task in request_iterator:
            self.db.put(new_task.key.encode(), new_task.data.encode())
            if new_task.data == self.db.get(new_task.key.encode()).decode():
                put_tasks.append(new_task)
            yield new_task

        # for i in put_tasks:
        #     print("Recorded task " + i.key + " " + i.data)

    def delete(self, request_iterator, context):
        for new_task in request_iterator:
            self.db.delete(new_task.key.encode())
            if self.db.get(new_task.key.encode()).decode() == None:
                print("Data Deleted" + new_task.key)
                delete_tasks.append(new_task)
            yield new_task


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