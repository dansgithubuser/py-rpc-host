import argparse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import inspect
import json
import os
from pprint import pprint
import sys
import uuid

parser = argparse.ArgumentParser()
parser.add_argument('module')
parser.add_argument('--port', default=8000)
args = parser.parse_args()

if args.module.endswith('.py'): args.module = args.module[:-3]
sys.path.append(os.path.dirname(args.module))
exec('import {} as module'.format(os.path.basename(args.module)))

store = {}

class Handler(BaseHTTPRequestHandler):
    def print_request_start(self):
        print('===== {} ====='.format(self.requestline))

    def parse(self):
        url_path = self.requestline.split()[1].split('/')[1:]
        command, attr_path = url_path[0], url_path[1:]
        attr = module
        for i in attr_path:
            if i: attr = getattr(attr, i)
        return (command, attr)

    def send_json_response(self, json_content=None):
        self.send_response(200)
        if json_content is not None:
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/javascript')
            self.end_headers()
            pprint(json_content)
            self.wfile.write(json.dumps(json_content).encode('utf-8'))

    def do_GET(self):
        self.print_request_start()
        command, attr = self.parse()
        if command == 'inspect':
            json_content = {
                'value': repr(attr),
                'dir': dir(attr),
            }
            try: json_content['args'] = repr(inspect.getargspec(attr))
            except: pass
        self.send_json_response(json_content)

    def do_POST(self):
        self.print_request_start()
        def parse_body():
            length = int(self.headers.get('Content-Length'))
            if length:
                kwargs = json.loads(self.rfile.read(length))
            else:
                kwargs = {}
            for k, v in kwargs.items():
                if v in store:
                    kwargs[k] = store[v]
            pprint(kwargs)
            return kwargs
        command, attr = self.parse()
        if command == 'store':
            id = str(uuid.uuid4())
            store[id] = attr(**parse_body())
            json_content = id
        elif command == 'get':
            json_content = attr(**parse_body())
        elif command == 'store-and-get':
            id = str(uuid.uuid4())
            value = attr(**parse_body())
            store[id] = value
            json_content = {'id': id, 'value': value}
        elif command == 'unstore':
            for i in json.loads(self.rfile.read()): del store[i]
            json_content = None
        self.send_json_response(json_content)

server_address = ('', int(args.port))
HTTPServer(server_address, Handler).serve_forever()
