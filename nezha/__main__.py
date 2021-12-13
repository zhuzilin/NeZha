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

from nezha.connection import run_host
from nezha.config_parser import parse_host_config


parser = argparse.ArgumentParser(description="Parse the config for NeZha")
parser.add_argument("-H", "--host_config", type=str, required=True)
parser.add_argument("-r", "--repl", action="store_true")
parser.add_argument("--file", type=str)
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

    def send_to_all(cmd):
        for i, conn in enumerate(send_conns):
            # Substitue "{NEZHA_ID}" with the process id, "{NEZHA_IP}" with its IP.
            cmd_i = cmd.format(NEZHA_ID=i, NEZHA_IP=hosts[i].ip)
            conn.send(cmd_i)

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
        if args.file is not None:
            if args.cmd is not None:
                logging.warning("File argument found. --cmd will be ignored.")
            with open(args.file, "r") as f:
                cmd = f.read()
            send_to_all(cmd)
            recv_from_all()
            send_to_all("exit")
            recv_from_all()
        elif args.cmd is not None:
            send_to_all(args.cmd)
            recv_from_all()
            send_to_all("exit")
            recv_from_all()
        else:
            raise RuntimeError(
                "Must provide command(--cmd) or command file(--file) when REPL is not used."
            )

    for p in processes:
        p.join()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
