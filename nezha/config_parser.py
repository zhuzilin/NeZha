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

import logging
from nezha.host import Host


def parse_host_config(filename):
    hosts = []
    with open(filename, "r") as f:
        host = None
        for line in f:
            line = line.strip()
            # Skip empty line or comment.
            if len(line) == 0 or line[0] == "#":
                continue
            segments = line.split()
            if len(segments) == 0:
                continue
            elif len(segments) != 2:
                raise RuntimeError(f"illegal config file: {line}")
            if segments[0].lower() == "host":
                if host is not None:
                    if host.user is None:
                        logging.info(
                            f"Host {host.name}'s user not set. Will use root as default."
                        )
                        host.user = "root"
                    if host.ip is None:
                        raise RuntimeError(f"Host {host.name}'s ip not set.")
                    hosts.append(host)

                name = segments[1]
                host = Host(name)
            else:
                if host is None:
                    raise RuntimeError(f"Must define host before setting value: {line}")
                if segments[0].lower() == "hostname":
                    host.ip = segments[1]
                elif segments[0].lower() == "user":
                    host.user = segments[1]
                elif segments[0].lower() == "port":
                    host.port = int(segments[1])
                else:
                    raise RuntimeError(f"Unknow key: {segments[0]}")
        if host is not None:
            hosts.append(host)
    return hosts
