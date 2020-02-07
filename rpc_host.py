from http.server import HTTPServer, BaseHTTPRequestHandler
import inspect
import json
import pdb
from pprint import pformat, pprint
import sys
import uuid

store = {}

class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'to_json'):
            return o.to_json()
        elif o.__class__ == bytes:
            return repr(o)
        else:
            super().default(o)

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
        attr = self.module
        for i in attr_name.split('.'):
            if not i: continue
            if i in store: attr = store[i]
            else: attr = getattr(attr, i)
        return (op, attr)

    def send_json_response(self, json_content=None):
        if json_content is None: json_content = {}
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/javascript')
        self.end_headers()
        pprint(json_content)
        self.wfile.write(JsonEncoder().encode(json_content).encode('utf-8'))

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
        elif op == 'get':
            json_content = attr
        elif op == 'pdb':
            pdb.set_trace()
            json_content = {}
        elif op == 'exit':
            self.send_json_response('exiting')
            sys.exit()
        self.send_json_response(json_content)

    def do_POST(self):
        self.print_request_start()
        def call(attr):
            args = []
            kwargs = {}
            length = int(self.headers.get('Content-Length'))
            if length:
                body = json.loads(self.rfile.read(length))
                pprint(body)
                for i in body:
                    if type(i) == list: args = i
                    else: kwargs = i
            for i, v in enumerate(args):
                if v in store:
                    args[i] = store[v]
            for k, v in kwargs.items():
                if v in store:
                    kwargs[k] = store[v]
            print('{}, {}'.format(pformat(args), pformat(kwargs)))
            return attr(*args, **kwargs)
        op, attr = self.parse()
        if op == 'store':
            id = str(uuid.uuid4())
            store[id] = call(attr)
            json_content = id
        elif op == 'eval':
            call(attr)
            json_content = None
        elif op == 'get':
            json_content = call(attr)
        elif op == 'unstore':
            for i in json.loads(self.rfile.read()): del store[i]
            json_content = None
        self.send_json_response(json_content)

def serve(module, port=8000):
    server_address = ('', port)
    class ModuleHandler(Handler): pass
    ModuleHandler.module = module
    HTTPServer(server_address, ModuleHandler).serve_forever()
