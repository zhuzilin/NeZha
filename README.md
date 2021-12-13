# NeZha (哪吒)

[NeZha](https://en.wikipedia.org/wiki/Nezha) is a famous chinese deity who can have three heads and six arms if he wants. And my NeZha tool is hoping to bring developer such multitask ability when handling multiple remote ssh servers.

NeZha is built upon [Fabric](https://github.com/fabric/fabric).

## Usage

NeZha will simultaneously connect the ssh servers you configed and run command on all of them.

To run certain command:

```bash
python3 -m nezha -H ./test_config --cmd pwd
```

And if you need different commands for different server, you can pass the command line as a format string in python:

```bash
python3 -m nezha -H ./test_config --cmd "echo {NEZHA_ID}"
```

The `{NEZHA_ID}` will be interpreted as 0 to n, corresponding the order of host in the host file (the file you send to `-H`). Other possible values are `{NEZHA_IP}`.

And you can run shell script with:

```bash
python3 -m nezha -H ./test_config --file test.sh
```

To use REPL:

```bash
python3 -m nezha -H ./test_config --repl
```

The `host_config`(`-H`) file should be similar to the ssh config, for example:

```
# lines started with hash sign will be treated as comment.
Host A
  User alice
  HostName 127.0.0.1

Host B
  User bob
  HostName 127.0.0.1
```
