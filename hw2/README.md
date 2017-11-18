# Hw2

1. Build Image

docker build -t 273web:1.0 .

2. Build Bridge

docker network create -d bridge --subnet 192.168.0.0/24 --gateway 192.168.0.1 dockernet

3. Generate Stub

docker run -it --rm --name grpc-tools -v "$PWD":/usr/src/myapp -w /usr/src/myapp 273web:1.0 python3.6 -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. datastore.proto

4. Server

docker run -p 3000:3000 -it --rm --name lab1-server -v "$PWD":/usr/src/myapp -w /usr/src/myapp 273web:1.0 python3.6 server.py

5. Client

docker run -it --rm --name lab1-client -v "$PWD":/usr/src/myapp -w /usr/src/myapp 273web:1.0 python3.6 client.py 192.168.0.1