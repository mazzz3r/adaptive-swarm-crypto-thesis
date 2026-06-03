# Adaptive Swarm Crypto Thesis

This repository contains the LaTeX source, final PDF, Russian annotation, and
benchmark artifacts for a thesis on adaptive lightweight secure communication
for swarm-oriented systems.

The practical part implements a pairwise benchmark prototype with static-heavy,
static-balanced, static-lightweight, and adaptive cryptographic profiles. The
benchmark is intentionally scoped to a constrained two-peer data path; it is not
a physical robot deployment or a validated large-swarm experiment.

## Repository Layout

- `thesis.tex`, `chapters/`, `ref.bib` - thesis source.
- `thesis.pdf` - compiled thesis deliverable.
- `annotation.tex`, `annotation.pdf` - Russian thesis annotation.
- `figs/` - figures used by the thesis.
- `benchmarks/src/` - executable benchmark package.
- `benchmarks/scenarios/` - scenario presets.
- `benchmarks/tests/` - unit and integration tests.
- `benchmarks/thesis-report-final/` - curated final benchmark matrix used by
  the thesis tables and figures.

Intermediate benchmark runs are ignored. Only the final curated matrix is kept
in Git so that the thesis results can be audited without carrying every local
experiment.

## Build the Thesis

Build the thesis PDF:

```sh
make pdf
```

Remove LaTeX auxiliary files and local Python caches while keeping the generated
PDF:

```sh
make clean
```

Remove auxiliary files, `thesis.pdf`, and local build folders:

```sh
make distclean
```

## Run Benchmark Tests

Run the benchmark test suite with the temporary uv environment used for this
project:

```sh
make test-bench
```

Docker-backed smoke tests are skipped unless explicitly enabled by the test
environment.

## Reproduce the Benchmark Report

From the `benchmarks` directory, run:

```sh
uv run bench thesis-report \
  --scenario scenarios/saturation-adaptive-long.yaml \
  --rates 25,50,75,100,150,200,300 \
  --duration-s 60 \
  --repeats 3 \
  --cpu-limits 0.05,0.10,0.25 \
  --rekey-intervals 2,5,10 \
  --network-profiles clean=0/0/0,mild=20/5/2,lossy=50/15/5 \
  --memory-limit-mb 128 \
  --output-dir thesis-report-final
```

The command produces aggregate CSV, JSON, Markdown, SVG, and PNG artifacts under
`benchmarks/thesis-report-final/comparison`, plus per-run summaries in timestamped
subdirectories.
