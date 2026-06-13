# Thesis Defense Presentation

A clean, minimalistic 12-slide deck for the bachelor's thesis
*Secure Communication Protocols for Swarm Robotics*.

- **Deliverable:** [`adaptive-swarm-crypto.pdf`](adaptive-swarm-crypto.pdf) — 12 slides, 16:9, paced for a ~10-minute defense.
- **Design:** ivory / brown palette (слоновая кость), low text, schematic-driven. Every figure is native vector drawing, so it stays crisp at any zoom.

## Slide flow

1. Title
2. Motivation — the security/performance trade-off
3. Aim & contributions
4. Formal model — dynamic graph + `F : S(t) → P`
5. Threat model & data-plane guarantees
6. Building blocks — the hybrid crypto stack
7. The three profiles (heavy / balanced / lightweight)
8. Adaptation logic — threshold decision tree
9. Benchmark testbed
10. Results I — crypto work & policy fit
11. Results II — CPU-limited saturation
12. Conclusion & future work

## Rebuild

The deck is generated programmatically with [`reportlab`](https://pypi.org/project/reportlab/):

```sh
pip install reportlab
python3 build_pdf.py   # -> adaptive-swarm-crypto.pdf
```

Fonts used (must be installed): Liberation Serif, Liberation Sans, DejaVu Sans Mono.
