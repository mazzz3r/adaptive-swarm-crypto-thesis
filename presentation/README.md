# Thesis Defense Presentation

Deck for the thesis *Secure Communication for Swarm Robotics*.

- [`adaptive-swarm-crypto.pdf`](adaptive-swarm-crypto.pdf) — the slides (12 + 1 Q&A backup, 16:9).

## Build

```sh
pip install reportlab
python3 build_pdf.py   # -> adaptive-swarm-crypto.pdf
```

Fonts are bundled in [`fonts/`](fonts), so the build is self-contained.
