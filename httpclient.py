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

    # get port number; 80 if None
    def get_host_port(self, url):
        # use port 80 designated for HTTP if none is provided
        return 80 if urllib.parse.urlparse(url).port is None else urllib.parse.urlparse(url).port

    # get path; "/" if None
    def get_path(self, urlParts):
        return "/" if not urlParts.path else urlParts.path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self, data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

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
        return buffer.decode('utf-8')

    def get_encoded_args(self, args):
        return "" if not args else urllib.parse.urlencode(args)

    def GET(self, url, args=None):
        # References: https://docs.python.org/3/library/urllib.parse.html
        # don't worry about args becuase its GET
        code = 500
        body = ""
        port = self.get_host_port(url)  # get port
        urlParts = urllib.parse.urlparse(url)  # all the parts in the url
        path = self.get_path(urlParts)  # get path
        self.connect(urlParts.hostname, port)  # make connection

        # standard POST request formatting, making sure to close after
        resultURL = f'''GET {path} HTTP/1.1\r\nHost: {urlParts.hostname}\r\nConnection: close\r\n\r\n'''
        self.sendall(resultURL)

        # read in the data
        readInInfo = self.recvall(self.socket)

        code = self.get_code(readInInfo)
        body = self.get_body(readInInfo)
        headers = self.get_headers(readInInfo)  # no need

        # close socket
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # References: https://docs.python.org/3/library/urllib.parse.html
        code = 500
        body = ""
        port = self.get_host_port(url)  # get port
        urlParts = urllib.parse.urlparse(url)  # all the parts in the url
        path = self.get_path(urlParts)  # get path
        self.connect(urlParts.hostname, port)  # make connection

        # get url encoded key value pair args
        args = self.get_encoded_args(args)

        # standard POST request formatting, making sure to close after
        self.sendall(
            f'''POST {path} HTTP/1.1\r\nHost: {urlParts.hostname}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(args)}\r\nConnection: close\r\n\r\n{args}''')
        # read in the data
        readInInfo = self.recvall(self.socket)

        code = self.get_code(readInInfo)
        body = self.get_body(readInInfo)
        headers = self.get_headers(readInInfo)  # no need

        # close socket
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
