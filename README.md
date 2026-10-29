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

![MapReduce flow](docs/mapreduce.gif)

Workers ask the coordinator for tasks. Maps write `mr-X-Y.json`; after
all maps finish, reduces read those and write `mr-out-Y`. Timed-out
tasks are retried by another worker.

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

### Re-render the animation

Uses [Manim Community](https://www.manim.community/) (`docs/manim/mapreduce.py`):

```bash
pyenv shell manim-env   # or any env with manim installed
cd docs/manim
manim -ql --format=gif -o mapreduce mapreduce.py MapReduceFlow
cp media/videos/mapreduce/480p15/mapreduce.gif ../mapreduce.gif
```

Use `-qm` instead of `-ql` for a sharper GIF.
