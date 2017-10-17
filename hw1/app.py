#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import random
import json
import rocksdb
import sys
from StringIO import StringIO

app = Flask(__name__)

@app.route('/api/v1/scripts', methods=['POST'])
def create_script():
    x = str(random.randint(10000, 99999))
    y = open("foo.py").read()
    db.put(x.encode(), y.encode())
    record = {
        'script-id': x
    }
    return jsonify(record), 201

@app.route('/api/v1/scripts/<script_id>', methods=['GET'])
def get_script(script_id):
    key = script_id
    result = db.get(key.encode())
    buffer = StringIO()
    sys.stdout = buffer
    exec(result)
    sys.stdout = sys.__stdout__
    return buffer.getvalue()

if __name__ == '__main__':
    db = rocksdb.DB("hw1.db", rocksdb.Options(create_if_missing=True))
    app.run(port=8000 ,debug=True)