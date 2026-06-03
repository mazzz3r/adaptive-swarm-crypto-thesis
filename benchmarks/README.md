# Diploma Benchmark Suite

This subproject contains the practical benchmark implementation for the diploma.
The measured data path is a constrained pairwise exchange between `peer_a` and `peer_b`.
Scenario files with `peer_count > 2` are illustrative workload presets, not validated multi-peer swarm experiments.

Run a scenario from this folder with:

```bash
uv run bench run --scenario scenarios/stable.yaml
```

To approximate weaker embedded hardware, cap each peer container explicitly:

```bash
uv run bench run --scenario scenarios/stable.yaml --cpu-limit-cores 0.50 --memory-limit-mb 256
```

To build a thesis-ready comparison from several completed runs:

```bash
uv run bench compare --results-root saturation-results
```

To run a rate sweep under the same CPU and memory cap:

```bash
uv run bench sweep --scenario scenarios/saturation-adaptive.yaml --rates 100,200,300 --cpu-limit-cores 0.05 --memory-limit-mb 128
```

To run the full thesis-friendly matrix with one command and get a ready report:

```bash
uv run bench thesis-report --output-dir thesis-report-final
```

The suite measures real host/container latency and throughput for the pairwise prototype. Energy remains a model-based estimate, while cryptographic work is derived from raw run counters and counts bytes processed by encryption, decryption, and authentication primitives.
The benchmark modes include `static-heavy`, `static-balanced`, `static-lightweight`, and `adaptive`. The `static-balanced` mode is useful as a middle baseline when the goal is to show how the adaptive policy differs from keeping the balanced profile fixed for the whole run.
The rate sweep should be interpreted as offered-load probing: under tight CPU caps the generator may not sustain the nominal message rate, so `attempted` and `delivered` rates must be read separately.

To generate the long-run policy trade-off figure without rerunning Docker:

```bash
uv run bench policy-tradeoff --scenario scenarios/saturation-adaptive-long.yaml --output-dir ../figs --filename benchmark_long_run_policy_tradeoff.png
```

The final thesis matrix runs repeated 60-second measurements by default:

```bash
uv run bench thesis-report \
  --scenario scenarios/saturation-adaptive-long.yaml \
  --rates 25,50,75,100,150,200,300 \
  --duration-s 60 \
  --repeats 3 \
  --cpu-limits 0.05,0.10,0.25 \
  --rekey-intervals 2,5,10 \
  --network-profiles clean=0/0/0,mild=20/5/2,lossy=50/15/5 \
  --memory-limit-mb 128 \
  --output-dir thesis-report-final \
  --no-build
```

This matrix is intentionally large: 228 runs at 60 seconds each before Docker setup overhead when all four modes are enabled.
Build the Docker images once before the full matrix, then use `--no-build` to avoid rebuilding before every individual run. If a long matrix is interrupted after some runs completed, repeat the same command with `--resume`; existing run directories with `summary.json` are skipped and only missing matrix cells are executed.
It produces aggregate report tables plus comparison, sweep, CPU sensitivity, rekey sensitivity, and network impairment plots under `thesis-report-final/comparison`.
