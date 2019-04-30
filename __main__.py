import argparse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import inspect
import json
import os
import pdb
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
        split = self.requestline.split()[1].split('/')[1:]
        op = split[0]
        if len(split) > 1:
            attr_name = split[1]
        else:
            attr_name = ''
        attr = module
        for i in attr_name.split('.'):
            if i: attr = getattr(attr, i)
        return (op, attr)

    def send_json_response(self, json_content=None):
        if json_content is None: json_content = {}
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/javascript')
        self.end_headers()
        pprint(json_content)
        self.wfile.write(json.dumps(json_content).encode('utf-8'))

    def do_GET(self):
        self.print_request_start()
        op, attr = self.parse()
        if op == 'inspect':
            json_content = {
                'value': repr(attr),
                'dir': dir(attr),
            }
            try: json_content['args'] = repr(inspect.getargspec(attr))
            except: pass
        elif op == 'pdb':
            pdb.set_trace()
            json_content = {}
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
        op, attr = self.parse()
        if op == 'store':
            id = str(uuid.uuid4())
            store[id] = attr(**parse_body())
            json_content = id
        elif op == 'eval':
            attr(**parse_body())
            json_content = None
        elif op == 'get':
            json_content = attr(**parse_body())
        elif op == 'unstore':
            for i in json.loads(self.rfile.read()): del store[i]
            json_content = None
        self.send_json_response(json_content)

server_address = ('', int(args.port))
HTTPServer(server_address, Handler).serve_forever()
