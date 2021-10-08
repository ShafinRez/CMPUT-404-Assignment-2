#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data[0].split(' ')[1]
        return int(code)

    def get_headers(self,data):
        headers = data[:len(data)]
        return headers

    def get_body(self, data):
        body = data[len(data)-1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        self.socket.shutdown(socket.SHUT_WR)
    
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8').split('\r\n')
        
    

    def GET(self, url, args=None):
    
        code = 500
        body = ""
        components = self.parse_url(url)
        path = components['path']
        host = components['host']
        port = components['port']
        
        self.connect(host, port)
        request = 'GET %s HTTP/1.1\r\nHost: %s\r\nConnection:closed\r\n\r\n' %(path,host)
        self.sendall(request)
        data = self.recvall(self.socket)
        
        if len(data) == 0:
            return  HTTPResponse(code, body)
        else:
            code = self.get_code(data)
            body = self.get_body(data)
            
        
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        
        code = 500
        body = ""
        components = self.parse_url(url)
        path = components['path']
        host = components['host']
        port = components['port']
        
        if args:
            arg_keys = list(args.keys())
            arg_vals = list(args.values())
    
            for i in range(len(args)):
                key_val =  arg_keys[i] + '=' + arg_vals[i]
                body += key_val + '&'
                        
        self.connect(host, port)
        request = 'POST %s HTTP/1.1\r\nHost: %s\r\nContent-Type:application/x-www-form-urlencoded\r\nContent-Length:%d\r\n\r\n%s' %(path,host,len(body),body)    
        self.sendall(request)
        data = self.recvall(self.socket)

        code = self.get_code(data)
        body = self.get_body(data)
        self.close()

        return HTTPResponse(code, body)

    
    def command(self, url, command="GET", args=None):
        
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
    def parse_url(self, url):
        url = urllib.parse.urlparse(url)
        path = '/'+ url.path
        hostName = url.netloc.split(':')[0]
        port = url.port
        if port == None:
            port = 80
        urlComponents = {'path':path, 'host':hostName, 'port':port}
        return urlComponents

    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    

    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
