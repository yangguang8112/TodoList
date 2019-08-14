#coding=utf-8
import argparse
import json
import os

from flask import Flask, g, jsonify, render_template, request, abort

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

# DB config
RDB_HOST = os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015
TODO_DB = 'todoapp'

# DB function
def dbSetup():
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)
    try:
        r.db_create(TODO_DB).run(connection)
        r.db(TODO_DB).table_create('todos').run(connection)
        print('数据库初始化完成。请不加--setup运行app')
    except RqlRuntimeError:
        print('数据库已存在。请不加--setup运行app')
    finally:
        connection.close()

# 创建app
app = Flask(__name__)
app.config.from_object(__name__)

# 管理连接
@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT, db=TODO_DB)
    except RqlDriverError:
        abort(503, "建立数据库连接失败!!")

@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass

# 列出存在的todo项目
@app.route("/todos", methods=['GET'])
def get_todos():
    selection = list(r.table('todos').run(g.rdb_conn))
    return json.dumps(selection)

# 创建一个todo项目
@app.route("/todos", methods=['POST'])
def new_todo():
    inserted = r.table('todos').insert(request.json).run(g.rdb_conn)
    return jsonify(id=inserted['generated_keys'][0])

# 检索单个todo
@app.route("/todos/<string:todo_id>", methods=['PUT'])
