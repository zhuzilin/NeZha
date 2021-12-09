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

import argparse
import logging
from multiprocessing import Pipe, Process

from connection import run_host
from config_parser import parse_host_config


parser = argparse.ArgumentParser(description="Parse the config for NeZha")
parser.add_argument("--host_config", type=str, required=True)
parser.add_argument("--repl", action="store_true")
parser.add_argument("--cmd", type=str)


def main():
    args = parser.parse_args()
    hosts = parse_host_config(args.host_config)
    processes = []
    send_conns = []
    recv_conns = []
    for host in hosts:
        parent_send_conn, child_recv_conn = Pipe()
        parent_recv_conn, child_send_conn = Pipe()
        p = Process(target=run_host, args=(host, child_recv_conn, child_send_conn))
        p.start()
        processes.append(p)
        send_conns.append(parent_send_conn)
        recv_conns.append(parent_recv_conn)

    def send_to_all(s):
        for conn in send_conns:
            conn.send(s)

    def recv_from_all():
        for conn in recv_conns:
            conn.recv()

    if args.repl:
        while True:
            print("NeZha >", end="")
            cmd = input("")
            send_to_all(cmd)
            recv_from_all()
            if cmd == "exit":
                break
    else:
        if args.cmd is None:
            raise RuntimeError("Must provide command(--cmd) when REPL is not used.")
        send_to_all(args.cmd)
        send_to_all("exit")

    for p in processes:
        p.join()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
