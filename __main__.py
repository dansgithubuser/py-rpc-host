import argparse
import os
import sys

import rpc_host

parser = argparse.ArgumentParser()
parser.add_argument('module')
parser.add_argument('--port', default=8000)
args = parser.parse_args()

if args.module.endswith('.py'): args.module = args.module[:-3]
sys.path.append(os.path.dirname(args.module))
exec('import {} as module'.format(os.path.basename(args.module)))
rpc_host.serve(module, int(args.port))
