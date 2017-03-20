from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
import sys
import random
import time
import json
import urllib2
import app_todomanager_config
from app_todomanager_config import docker_host_ip


self_debug = 1

app = Flask(__name__)
api = Api(app)

todos = {}
app_id = random.randint(1,11)

#ETCD
etcd_dict = {} 

#Add bogus entry
etcd_dict[app_todomanager_config.timeapp_url] = 'http://127.0.0.1:8000/time1'

def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in todos:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')


# Todo
# shows a single todo item and lets you delete a todo item
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        if(self_debug):
            print "\nApp Instance: %d processing GET"%(app_id)
        return todos[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del todos[todo_id]
        return '', 204

    def put(self, todo_id):
        if(self_debug):
            print "\nApp Instance: %d processing PUT"%(app_id)

        #Get current time from microservice timeapp
        if(self_debug):
            print 'Get time from URL:%s'%(etcd_dict[app_todomanager_config.timeapp_url])
        time_nvpair = json.load(urllib2.urlopen(etcd_dict[app_todomanager_config.timeapp_url]))
        time_val = time_nvpair['time']
        #time_val = '01-01-01 1970'

        #Get timezone from collaborating peer service
        tz_nvpair = json.load(urllib2.urlopen(app_todomanager_config.tzpeer_url))
        tz_val = tz_nvpair['tz']

        args = parser.parse_args()
        todo_item_timed = time_val + ' ' + tz_val + ' ' + args['task']
        task = {'task': todo_item_timed}


        todos[todo_id] = task
        return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return todos

    def post(self):
        if(self_debug):
            print "\nApp Instance: %d processing PUT"%(app_id)

        #Get current time from microservice timeapp
        if(self_debug):
            print 'Get time from URL:%s'%(etcd_dict[app_todomanager_config.timeapp_url])
        time_nvpair = json.load(urllib2.urlopen(etcd_dict[app_todomanager_config.timeapp_url]))
        time_val = time_nvpair['time']
        #time_val = '01-01-01 1970'

        #Get timezone from collaborating peer service
        tz_nvpair = json.load(urllib2.urlopen(app_todomanager_config.tzpeer_url))
        tz_val = tz_nvpair['tz']

        args = parser.parse_args()
        if(len(todos)):
            todo_index = int(max(todos.keys()).lstrip('todo')) + 1
        else:
            todo_index = 1
        todo_id = 'todo%i' % todo_index
        todos[todo_id] = {'task': args['task']}
        return todos[todo_id], 201

##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todo')
api.add_resource(Todo, '/todo/<todo_id>')


if __name__ == '__main__':

    if(len(sys.argv) == 3):
        run_port = sys.argv[1]
        etcd_dict[app_todomanager_config.timeapp_url] = sys.argv[2]
    else:
        run_port = 6000

    print etcd_dict

    app.run(host=docker_host_ip,port=int(run_port), debug=True)
