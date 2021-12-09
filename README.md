# NeZha (哪吒)

[NeZha](https://en.wikipedia.org/wiki/Nezha) is a famous chinese deity who can have three heads and six arms if he wants. And my NeZha tool is hoping to bring developer such multitask ability when handling multiple remote remote servers.

NeZha is built upon [Fabric](https://github.com/fabric/fabric).

To use REPL:

```bash
python3 -m nezha --host_config ./test_config --repl
```

To run certain command:

```bash
python3 -m nezha --host_config ./test_config --cmd pwd
```

The `host_config` file should be similar to the ssh config, for example:

```
Host A
  User alice
  HostName 127.0.0.1

Host B
  User bob
  HostName 127.0.0.1
```
