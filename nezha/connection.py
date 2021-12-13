# Copyright 2021 zhuzilin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import logging
from multiprocessing import log_to_stderr
from multiprocessing.connection import Connection
import fabric

from nezha.context import Context
from nezha.host import Host


def connect(host: Host):
    connection = fabric.Connection(host.ip, host.port, host.port)
    logging.info(f"Connect to host {host}")
    return connection


def format_output(s: str, host: Host):
    name = host.name
    # Remove the last endline
    lines = s.split("\n")[:-1]
    formated_lines = []
    for line in lines:
        formated_lines.append(f"[{name}] {line}")
    return "\n".join(formated_lines)


def print_format(s: str, host: Host):
    print(format_output(s, host))


def run_host(host: Host, recv_conn: Connection, send_conn: Connection):
    log_to_stderr(logging.DEBUG)

    connection = connect(host)
    context = Context()
    exited = False
    while not exited:
        # TODO(zhuzilin) support multiline command
        cmds = recv_conn.recv().strip().split("\n")
        for cmd in cmds:
            cmd = cmd.strip().split()
            if len(cmd) == 0:
                pass
            elif cmd[0] == "exit":
                send_conn.send("")
                exited = True
                break
            elif cmd[0] == "cd":
                path = cmd[1]
                if os.path.isabs(path):
                    context.path = path
                else:
                    context.path = os.path.join(context.path, path)
            else:
                try:
                    with connection.cd(context.path):
                        connection.run(" ".join(cmd), hide=False)
                except:  # noqa: E722
                    print_format(f"Failed to execute cmd {cmd}", host)
        send_conn.send("")
    connection.close()
