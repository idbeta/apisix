#!/usr/bin/env bash
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#! /usr/bin/env python
import subprocess
from boofuzz import *

def create_route():
    command = '''curl http://127.0.0.1:9080/apisix/admin/routes/1 -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' -X PUT -d '
{
    "uri": "/get*",
    "methods": ["GET"],
    "upstream": {
        "type": "roundrobin",
        "nodes": {
            "127.0.0.1:6666": 1
        }
    }
}'
    '''
    r = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    print(r.stdout.read())

def main():
    fw = open(r'test.log','wb')
    session = Session(
        target=Target(
            connection=TCPSocketConnection("127.0.0.1", 9080, send_timeout=5.0, recv_timeout=5.0, server=False)  
        ),
        sleep_time=0.1,
    )

    s_initialize(name="Request")
    with s_block("Request-Line"):
        s_group("Method", ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE'])
        s_delim(" ", name='space-1')
        s_string("/get", name='Request-URI')
        s_delim(" ", name='space-2')
        s_string('HTTP/1.1', name='HTTP-Version')
        s_static("\r\n", name="Request-Line-CRLF")
        s_string("Host:", name="Host-Line")
        s_delim(" ", name="space-3")
        s_string("example.com", name="Host-Line-Value")
        s_static("\r\n", name="Host-Line-CRLF")
        s_string("Connection:", name="Connection-Line")
        s_delim(" ", name="space-4")
        s_string("Keep-Alive", name="Connection-Line-Value")
        s_static("\r\n", name="Connection-Line-CRLF")
        s_string("User-Agent:", name="User-Agent-Line")
        s_delim(" ", name="space-5")
        s_string("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1", name="User-Agent-Line-Value")
        s_static("\r\n", name="User-Agent-Line-CRLF")

    s_static("\r\n", "Request-CRLF")

    session.connect(s_get("Request"))

    session.fuzz()


if __name__ == "__main__":
    create_route()
    main()
