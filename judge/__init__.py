'Online Judge'


import hashlib
import os
import socketserver
import subprocess
import threading
import time
import xmlrpc.server



class Thread(threading.Thread):
    'Subclass of threading.Thread with return value'
    return_value = None
    def run(self):
        try:
            if self._target:
                self.return_value = self._target(*self._args, **self._kwargs)
        finally:
            del self._target, self._args, self._kwargs


def _judge(filename, stdin, stdout, timeout):
    "Run './filename' with the input data and check if its output is the same as the given"
    start = time.time()
    try:
        if subprocess.run(os.path.join('.', filename), input=stdin.encode(), capture_output=True,
                          timeout=timeout, check=True).stdout.decode().rstrip() == stdout.rstrip():
            return 'AC', time.time() - start
        return 'WA', time.time() - start
    except (subprocess.TimeoutExpired, ValueError):
        return 'TLE', timeout
    except subprocess.CalledProcessError:
        return 'RE', time.time() - start


def judge(source, data, timeout=1, quiet=False):
    "Compile the source file and call '_judge' with input and output data of each test point"
    assert timeout <= 60, 'Time limit exceeded'
    md5 = hashlib.md5(source.encode()).hexdigest()
    # print(md5)
    with open(str(md5) + '.cpp', 'w') as file:
        file.write(source)
    try:
        subprocess.run(['g++', str(md5) + '.cpp', '-o', str(md5)], capture_output=quiet, check=True)
    except subprocess.CalledProcessError:
        return 'CE'
    # finally:
    #     os.remove(str(md5) + '.cpp')
    threads = []
    for stdin, stdout in data:
        threads.append(Thread(target=_judge, args=(str(md5), stdin, stdout, timeout)))
        threads[-1].start()
    result = ([], [])
    for thread in threads:
        thread.join()
        result[0].append(thread.return_value[0])
        result[1].append(round(thread.return_value[1] * 1000))
    # print(result[1])
    os.remove(str(md5))
    return result


class Server(socketserver.ThreadingMixIn, xmlrpc.server.SimpleXMLRPCServer):
    'Threading version of xmlrpc.server.SimpleXMLRPCServer'


# class RequestHandler(xmlrpc.server.SimpleXMLRPCRequestHandler):
#     rpc_paths = ('/', '/RPC2')


def main(port=8000, address='', quiet=False):
    'if __name__ == __main__'
    with Server((address, port), xmlrpc.server.SimpleXMLRPCRequestHandler, not quiet) as server:
        server.register_function(judge)
        if not quiet:
            print('Serving XML-RPC on', address or 'localhost', 'port', port)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print()
            if not quiet:
                print("Keyboard interrupt received, exiting.")


if __name__ == '__main__':
    main(int(input('Port: ')), input("Address (Default to 'localhost'): "))
