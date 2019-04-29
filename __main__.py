import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import inspect
import json
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument('module')
parser.add_argument('--port', default=8000)
args = parser.parse_args()

if args.module.endswith('.py'): args.module = args.module[:-3]
sys.path.append(os.path.dirname(args.module))
exec('import {} as module'.format(os.path.basename(args.module)))

def parse_requestline(r): return r.split()[1].split('/')[1:]

class Handler(BaseHTTPRequestHandler):
    def send_json_response(self, j):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(j).encode('utf-8'))

    def do_GET(self):
        path = parse_requestline(self.requestline)
        print('path: {}, requestline: {}'.format(path, self.requestline))
        x = module
        for i in path:
            if i: x = getattr(x, i)
        r = {
            'value': repr(x),
            'type': repr(type(x)),
            'dir': dir(x),
        }
        try:
            r['args'] = repr(inspect.getargspec(x))
        except: pass
        self.send_json_response(r)

'''
post /expression
    eval(expression)(a1=a1, a2=a2...)
    returns id that can be referenced

post /id/expression
    get result corresponding to expression/id
    returns 
'''

server_address = ('', int(args.port))
HTTPServer(server_address, Handler).serve_forever()
