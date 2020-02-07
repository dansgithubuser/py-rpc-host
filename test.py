import subprocess
import threading
import time
from urllib.request import urlopen

def section(topic):
    print('/' + '‾'*40)
    print('  ' + topic)
    print('_'*40 + '/')

def test_rpc_host():
    time.sleep(1)
    response = urlopen('http://localhost:8000/get/blinger')
    assert response.read().decode() == '24'
    urlopen('http://localhost:8000/exit')
    time.sleep(1)

section('testing command line')
subprocess.Popen(['python', '../py-rpc-host', 'thinger.py'])
test_rpc_host()

section('testing programmatic')
subprocess.Popen(['python', 'programmatic.py'])
test_rpc_host()
