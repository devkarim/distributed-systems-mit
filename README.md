# Distributed Systems (MIT 6.5840)

Solutions for [MIT 6.5840](https://pdos.csail.mit.edu/6.5840/) labs in Go.

## Labs

| Lab | Directory | Status |
|-----|-----------|--------|
| MapReduce | `src/mr` | Done |
| Key/Value Server | `src/kvsrv1` | — |
| Raft | `src/raft1` | — |
| Fault-tolerant KV | `src/kvraft1` | — |
| Sharded KV | `src/shardkv1` | — |

## MapReduce

```bash
cd src
make mr                  # full test suite
make RUN='-run TestWc' mr
```

Manual run (debug logs on by default):

```bash
./run-mr.sh              # coordinator
./run-mr-worker.sh       # worker (separate terminal)
```

Unset `MR_DEBUG` to silence logs: `MR_DEBUG= ./run-mr.sh`.

On macOS, plugins are built with `-ldflags=-w` so dyld can load them.
