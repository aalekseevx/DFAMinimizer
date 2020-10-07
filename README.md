# DFA Minimizer

[![codecov](https://codecov.io/gh/aalekseevx/DFAMinimizer/branch/master/graph/badge.svg)](https://codecov.io/gh/aalekseevx/DFAMinimizer)

Script, which makes finite automation deterministic and
minimizes it if possible.

## Requirements

- Poetry 1.1.0

All the other staff will be installed with

```bash
poetry install
```

## Run program

`dfa.json` is an input file, formatted as `dfa_example.json`.
```bash
poetry run task main dfa.json small_dfa.json
```

## Run tests

```bash
poetry run task test
```
