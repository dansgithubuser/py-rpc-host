py-rpc-host allows a developer to quickly turn a Python module into an HTTP server.

## usage
There are two ways to use py-rpc-host: from the command line, and programmatically. In the below examples, we assume the existence of a module `thinger.py` that contains a variable `blinger = 24`. Such a module exists in this repo and the examples below can be tested by running `test.py`.

### command line
shell:
```
python py-rpc-host thinger.py
```

### programmatic
Python:
```
import rpc_host
import thinger

rpc_host.serve(thinger)
```

### browser
In either case, once the server is running, navigate to `localhost:8000/get/blinger` to see the result 24.

## more
To see the full set of features available, look in `rpc_host.py`, `Handler` class, `parse`, `do_GET`, and `do_POST` methods.
