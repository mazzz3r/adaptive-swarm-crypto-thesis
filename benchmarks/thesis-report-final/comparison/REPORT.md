# Thesis Benchmark Report

## Setup

- CPU cap per peer: `0.05` cores
- Memory cap per peer: `128` MiB
- Message size: `65536` bytes
- Peer count: `2`
- Traffic pattern: `peer_a -> peer_b` pairwise exchange; extra peers are not part of the measured data path.

## Key Finding

Under constrained compute, the end-to-end throughput curves are dominated by the shared containerized transport and CPU cap. Profile differences are therefore reported separately through cryptographic work: bytes processed by encryption, decryption, and authentication primitives. Lightweight has the lowest cryptographic work per delivered message, heavy has the highest, and adaptive remains between the static extremes. The sweep should be read as offered-load probes against the same pairwise prototype, not as validated multi-peer swarm scaling.

## Main Stability Sweep

| Offered rate | Mode | Runs | Median P50 (ms) | Median P95 (ms) | Median P99 (ms) | Median throughput | Median drop % | Median crypto work (MiB/msg) | Median energy/msg | Throughput std |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 25 | Adaptive | 3 | 25.296 | 202.027 | 301.172 | 25.0 | 0.000 | 0.2248 | 13.5043 | 0.02 |
| 25 | static-balanced | 3 | 12.422 | 199.912 | 298.894 | 25.0 | 0.000 | 0.2500 | 13.4567 | 0.00 |
| 25 | Heavy | 3 | 77.606 | 294.362 | 397.421 | 25.0 | 0.000 | 0.2500 | 13.6214 | 0.00 |
| 25 | Lightweight | 3 | 30.701 | 202.364 | 304.612 | 25.0 | 0.000 | 0.1251 | 13.3568 | 0.01 |
| 50 | Adaptive | 3 | 100.938 | 695.493 | 898.012 | 46.9 | 6.175 | 0.2240 | 13.4260 | 2.30 |
| 50 | static-balanced | 3 | 178.694 | 695.961 | 798.890 | 47.6 | 4.447 | 0.2500 | 13.3766 | 2.00 |
| 50 | Heavy | 3 | 197.992 | 543.232 | 795.484 | 46.3 | 6.877 | 0.2500 | 13.5490 | 0.35 |
| 50 | Lightweight | 3 | 101.445 | 546.791 | 699.806 | 47.7 | 4.167 | 0.1251 | 13.2789 | 0.24 |
| 75 | Adaptive | 3 | 141.028 | 597.793 | 798.515 | 53.7 | 27.923 | 0.2257 | 13.4206 | 2.10 |
| 75 | static-balanced | 3 | 101.597 | 403.873 | 701.058 | 54.1 | 26.443 | 0.2500 | 13.3674 | 6.53 |
| 75 | Heavy | 3 | 198.307 | 697.320 | 825.192 | 56.7 | 24.356 | 0.2500 | 13.5343 | 0.38 |
| 75 | Lightweight | 3 | 101.698 | 596.553 | 774.667 | 57.2 | 23.489 | 0.1251 | 13.2637 | 0.58 |
| 100 | Adaptive | 3 | 195.263 | 599.890 | 752.292 | 61.2 | 38.783 | 0.2256 | 13.4085 | 1.56 |
| 100 | static-balanced | 3 | 102.750 | 500.696 | 700.531 | 59.9 | 38.484 | 0.2500 | 13.3608 | 2.67 |
| 100 | Heavy | 3 | 124.843 | 571.559 | 825.390 | 58.4 | 40.110 | 0.2500 | 13.5311 | 0.79 |
| 100 | Lightweight | 3 | 128.887 | 694.480 | 800.385 | 62.7 | 36.206 | 0.1251 | 13.2580 | 2.60 |
| 150 | Adaptive | 3 | 103.044 | 496.674 | 699.220 | 58.7 | 58.410 | 0.2221 | 13.4079 | 4.61 |
| 150 | static-balanced | 3 | 196.844 | 601.281 | 798.638 | 68.0 | 54.189 | 0.2500 | 13.3535 | 4.77 |
| 150 | Heavy | 3 | 102.715 | 695.176 | 896.869 | 67.0 | 54.025 | 0.2500 | 13.5225 | 2.78 |
| 150 | Lightweight | 3 | 201.109 | 601.308 | 795.585 | 56.5 | 60.181 | 0.1251 | 13.2626 | 1.42 |
| 200 | Adaptive | 3 | 199.721 | 699.131 | 902.077 | 59.6 | 69.764 | 0.2243 | 13.4100 | 1.01 |
| 200 | static-balanced | 3 | 201.448 | 797.382 | 963.524 | 61.2 | 67.627 | 0.2500 | 13.3594 | 1.34 |
| 200 | Heavy | 3 | 200.797 | 697.407 | 901.111 | 60.9 | 68.615 | 0.2500 | 13.5276 | 1.30 |
| 200 | Lightweight | 3 | 198.301 | 700.638 | 896.513 | 63.9 | 67.776 | 0.1251 | 13.2553 | 2.21 |
| 300 | Adaptive | 3 | 199.256 | 697.619 | 899.595 | 63.7 | 78.447 | 0.2230 | 13.3969 | 2.58 |
| 300 | static-balanced | 3 | 200.033 | 695.980 | 895.410 | 63.1 | 78.873 | 0.2500 | 13.3564 | 0.86 |
| 300 | Heavy | 3 | 198.630 | 699.370 | 898.656 | 62.0 | 77.631 | 0.2500 | 13.5267 | 1.10 |
| 300 | Lightweight | 3 | 198.126 | 795.373 | 901.518 | 61.0 | 75.341 | 0.1251 | 13.2576 | 1.90 |

## Individual Rate Runs

| Group | Offered rate | Attempted rate | Mode | Repeat | P50 latency (ms) | Throughput (msg/s) | Drop % | Crypto work (MiB/msg) | Energy / delivered message |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cpu-sensitivity | 100 | 93.6 | Adaptive | 1 | 198.901 | 52.5 | 43.926 | 0.2234 | 13.4186 |
| cpu-sensitivity | 100 | 99.9 | Adaptive | 1 | 17.100 | 99.9 | 0.000 | 0.2250 | 13.3900 |
| cpu-sensitivity | 100 | 100.0 | Adaptive | 1 | 2.693 | 100.0 | 0.000 | 0.2250 | 13.3927 |
| cpu-sensitivity | 100 | 99.3 | Adaptive | 2 | 199.435 | 54.2 | 45.410 | 0.2211 | 13.4031 |
| cpu-sensitivity | 100 | 100.0 | Adaptive | 2 | 92.215 | 99.9 | 0.133 | 0.2250 | 13.3905 |
| cpu-sensitivity | 100 | 100.0 | Adaptive | 2 | 2.729 | 100.0 | 0.000 | 0.2250 | 13.3930 |
| cpu-sensitivity | 100 | 100.0 | Adaptive | 3 | 197.641 | 59.9 | 40.067 | 0.2233 | 13.4066 |
| cpu-sensitivity | 100 | 99.8 | Adaptive | 3 | 86.256 | 99.7 | 0.117 | 0.2248 | 13.3898 |
| cpu-sensitivity | 100 | 100.0 | Adaptive | 3 | 2.654 | 100.0 | 0.000 | 0.2250 | 13.3927 |
| cpu-sensitivity | 100 | 100.0 | static-balanced | 1 | 297.069 | 61.2 | 38.740 | 0.2500 | 13.3573 |
| cpu-sensitivity | 100 | 99.9 | static-balanced | 1 | 4.175 | 99.9 | 0.000 | 0.2500 | 13.3421 |
| cpu-sensitivity | 100 | 100.0 | static-balanced | 1 | 2.723 | 100.0 | 0.000 | 0.2500 | 13.3449 |
| cpu-sensitivity | 100 | 97.8 | static-balanced | 2 | 296.837 | 57.3 | 41.428 | 0.2500 | 13.3613 |
| cpu-sensitivity | 100 | 100.0 | static-balanced | 2 | 91.797 | 100.0 | 0.000 | 0.2500 | 13.3408 |
| cpu-sensitivity | 100 | 100.0 | static-balanced | 2 | 2.755 | 100.0 | 0.000 | 0.2500 | 13.3449 |
| cpu-sensitivity | 100 | 97.2 | static-balanced | 3 | 200.203 | 53.1 | 45.364 | 0.2500 | 13.3686 |
| cpu-sensitivity | 100 | 100.0 | static-balanced | 3 | 90.508 | 100.0 | 0.000 | 0.2500 | 13.3422 |
| cpu-sensitivity | 100 | 100.0 | static-balanced | 3 | 2.753 | 100.0 | 0.000 | 0.2500 | 13.3448 |
| cpu-sensitivity | 100 | 97.9 | Heavy | 1 | 202.771 | 50.5 | 48.459 | 0.2500 | 13.5398 |
| cpu-sensitivity | 100 | 99.9 | Heavy | 1 | 92.666 | 99.8 | 0.133 | 0.2500 | 13.5109 |
| cpu-sensitivity | 100 | 100.0 | Heavy | 1 | 2.686 | 100.0 | 0.000 | 0.2500 | 13.5147 |
| cpu-sensitivity | 100 | 99.5 | Heavy | 2 | 200.485 | 53.7 | 46.056 | 0.2500 | 13.5355 |
| cpu-sensitivity | 100 | 99.9 | Heavy | 2 | 93.668 | 99.9 | 0.000 | 0.2500 | 13.5122 |
| cpu-sensitivity | 100 | 100.0 | Heavy | 2 | 2.692 | 100.0 | 0.000 | 0.2500 | 13.5147 |
| cpu-sensitivity | 100 | 99.2 | Heavy | 3 | 199.330 | 57.1 | 42.425 | 0.2500 | 13.5340 |
| cpu-sensitivity | 100 | 100.0 | Heavy | 3 | 95.918 | 100.0 | 0.000 | 0.2500 | 13.5108 |
| cpu-sensitivity | 100 | 100.0 | Heavy | 3 | 2.635 | 100.0 | 0.000 | 0.2500 | 13.5144 |
| cpu-sensitivity | 100 | 97.4 | Lightweight | 1 | 200.844 | 52.0 | 46.604 | 0.1251 | 13.2677 |
| cpu-sensitivity | 100 | 100.0 | Lightweight | 1 | 2.883 | 100.0 | 0.000 | 0.1251 | 13.2420 |
| cpu-sensitivity | 100 | 100.0 | Lightweight | 1 | 2.695 | 100.0 | 0.000 | 0.1251 | 13.2448 |
| cpu-sensitivity | 100 | 95.2 | Lightweight | 2 | 200.562 | 53.5 | 43.768 | 0.1251 | 13.2683 |
| cpu-sensitivity | 100 | 100.0 | Lightweight | 2 | 17.902 | 100.0 | 0.000 | 0.1251 | 13.2421 |
| cpu-sensitivity | 100 | 100.0 | Lightweight | 2 | 2.624 | 100.0 | 0.000 | 0.1251 | 13.2445 |
| cpu-sensitivity | 100 | 99.2 | Lightweight | 3 | 197.196 | 57.0 | 42.504 | 0.1251 | 13.2640 |
| cpu-sensitivity | 100 | 100.0 | Lightweight | 3 | 3.065 | 100.0 | 0.000 | 0.1251 | 13.2421 |
| cpu-sensitivity | 100 | 100.0 | Lightweight | 3 | 2.711 | 100.0 | 0.000 | 0.1251 | 13.2451 |
| cpu-sensitivity | 200 | 191.0 | Adaptive | 1 | 195.289 | 76.4 | 60.010 | 0.2265 | 13.3908 |
| cpu-sensitivity | 200 | 200.0 | Adaptive | 1 | 96.506 | 148.4 | 25.792 | 0.2252 | 13.3743 |
| cpu-sensitivity | 200 | 200.0 | Adaptive | 1 | 1.079 | 200.0 | 0.000 | 0.2250 | 13.3704 |
| cpu-sensitivity | 200 | 200.0 | Adaptive | 2 | 199.009 | 65.2 | 67.417 | 0.2268 | 13.3975 |
| cpu-sensitivity | 200 | 198.9 | Adaptive | 2 | 97.313 | 155.4 | 21.873 | 0.2267 | 13.3760 |
| cpu-sensitivity | 200 | 200.0 | Adaptive | 2 | 1.093 | 199.1 | 0.467 | 0.2249 | 13.3699 |
| cpu-sensitivity | 200 | 200.0 | Adaptive | 3 | 128.492 | 76.8 | 61.585 | 0.2201 | 13.3811 |
| cpu-sensitivity | 200 | 198.0 | Adaptive | 3 | 95.796 | 155.9 | 21.293 | 0.2248 | 13.3726 |
| cpu-sensitivity | 200 | 200.0 | Adaptive | 3 | 1.147 | 200.0 | 0.000 | 0.2250 | 13.3705 |
| cpu-sensitivity | 200 | 191.5 | static-balanced | 1 | 101.843 | 63.5 | 66.832 | 0.2500 | 13.3594 |
| cpu-sensitivity | 200 | 199.8 | static-balanced | 1 | 97.338 | 151.9 | 23.930 | 0.2500 | 13.3267 |
| cpu-sensitivity | 200 | 200.0 | static-balanced | 1 | 1.085 | 200.0 | 0.000 | 0.2500 | 13.3223 |
| cpu-sensitivity | 200 | 200.0 | static-balanced | 2 | 201.149 | 68.0 | 66.000 | 0.2500 | 13.3517 |
| cpu-sensitivity | 200 | 200.0 | static-balanced | 2 | 96.721 | 151.4 | 24.290 | 0.2500 | 13.3268 |
| cpu-sensitivity | 200 | 200.0 | static-balanced | 2 | 1.169 | 200.0 | 0.000 | 0.2500 | 13.3225 |
| cpu-sensitivity | 200 | 198.2 | static-balanced | 3 | 103.972 | 65.7 | 66.843 | 0.2500 | 13.3554 |
| cpu-sensitivity | 200 | 198.4 | static-balanced | 3 | 96.528 | 153.2 | 22.777 | 0.2500 | 13.3265 |
| cpu-sensitivity | 200 | 200.0 | static-balanced | 3 | 1.156 | 200.0 | 0.000 | 0.2500 | 13.3225 |
| cpu-sensitivity | 200 | 200.0 | Heavy | 1 | 198.387 | 57.3 | 71.350 | 0.2500 | 13.5338 |
| cpu-sensitivity | 200 | 199.5 | Heavy | 1 | 97.266 | 147.7 | 26.002 | 0.2500 | 13.4976 |
| cpu-sensitivity | 200 | 200.0 | Heavy | 1 | 1.046 | 200.0 | 0.000 | 0.2500 | 13.4922 |
| cpu-sensitivity | 200 | 194.3 | Heavy | 2 | 198.708 | 60.5 | 68.860 | 0.2500 | 13.5280 |
| cpu-sensitivity | 200 | 199.9 | Heavy | 2 | 96.653 | 148.3 | 25.821 | 0.2500 | 13.4974 |
| cpu-sensitivity | 200 | 200.0 | Heavy | 2 | 1.062 | 200.0 | 0.000 | 0.2500 | 13.4922 |
| cpu-sensitivity | 200 | 191.9 | Heavy | 3 | 101.953 | 62.5 | 67.448 | 0.2500 | 13.5304 |
| cpu-sensitivity | 200 | 198.7 | Heavy | 3 | 97.300 | 146.8 | 26.105 | 0.2500 | 13.4977 |
| cpu-sensitivity | 200 | 200.0 | Heavy | 3 | 1.097 | 200.0 | 0.000 | 0.2500 | 13.4923 |
| cpu-sensitivity | 200 | 198.6 | Lightweight | 1 | 194.513 | 69.5 | 65.022 | 0.1251 | 13.2506 |
| cpu-sensitivity | 200 | 197.4 | Lightweight | 1 | 98.679 | 153.1 | 22.445 | 0.1251 | 13.2265 |
| cpu-sensitivity | 200 | 200.0 | Lightweight | 1 | 1.118 | 200.0 | 0.000 | 0.1251 | 13.2225 |
| cpu-sensitivity | 200 | 197.4 | Lightweight | 2 | 101.519 | 69.8 | 64.612 | 0.1251 | 13.2522 |
| cpu-sensitivity | 200 | 198.6 | Lightweight | 2 | 94.957 | 147.7 | 25.619 | 0.1251 | 13.2284 |
| cpu-sensitivity | 200 | 200.0 | Lightweight | 2 | 1.138 | 200.0 | 0.000 | 0.1251 | 13.2225 |
| cpu-sensitivity | 200 | 199.3 | Lightweight | 3 | 198.131 | 71.0 | 64.356 | 0.1251 | 13.2494 |
| cpu-sensitivity | 200 | 199.6 | Lightweight | 3 | 97.791 | 151.2 | 24.204 | 0.1251 | 13.2269 |
| cpu-sensitivity | 200 | 200.0 | Lightweight | 3 | 1.196 | 200.0 | 0.000 | 0.1251 | 13.2226 |
| main-stability | 25 | 25.0 | Adaptive | 1 | 4.473 | 25.0 | 0.000 | 0.2248 | 13.5043 |
| main-stability | 25 | 25.0 | Adaptive | 2 | 25.296 | 25.0 | 0.000 | 0.2244 | 13.5039 |
| main-stability | 25 | 25.0 | Adaptive | 3 | 71.528 | 25.0 | 0.000 | 0.2250 | 13.5044 |
| main-stability | 25 | 25.0 | static-balanced | 1 | 26.528 | 25.0 | 0.000 | 0.2500 | 13.4569 |
| main-stability | 25 | 25.0 | static-balanced | 2 | 12.422 | 25.0 | 0.000 | 0.2500 | 13.4567 |
| main-stability | 25 | 25.0 | static-balanced | 3 | 3.444 | 25.0 | 0.000 | 0.2500 | 13.4567 |
| main-stability | 25 | 25.0 | Heavy | 1 | 95.576 | 25.0 | 0.000 | 0.2500 | 13.6214 |
| main-stability | 25 | 25.0 | Heavy | 2 | 77.606 | 25.0 | 0.000 | 0.2500 | 13.6211 |
| main-stability | 25 | 25.0 | Heavy | 3 | 11.348 | 25.0 | 0.000 | 0.2500 | 13.6267 |
| main-stability | 25 | 25.0 | Lightweight | 1 | 30.701 | 25.0 | 0.000 | 0.1251 | 13.3569 |
| main-stability | 25 | 25.0 | Lightweight | 2 | 16.075 | 25.0 | 0.000 | 0.1251 | 13.3567 |
| main-stability | 25 | 25.0 | Lightweight | 3 | 32.786 | 25.0 | 0.000 | 0.1251 | 13.3568 |
| main-stability | 50 | 49.9 | Adaptive | 1 | 100.938 | 46.9 | 6.175 | 0.2239 | 13.4260 |
| main-stability | 50 | 49.5 | Adaptive | 2 | 100.722 | 47.4 | 4.146 | 0.2240 | 13.4242 |
| main-stability | 50 | 49.7 | Adaptive | 3 | 196.707 | 43.2 | 13.116 | 0.2241 | 13.4305 |
| main-stability | 50 | 49.9 | static-balanced | 1 | 178.694 | 47.6 | 4.447 | 0.2500 | 13.3766 |
| main-stability | 50 | 49.9 | static-balanced | 2 | 102.334 | 48.0 | 3.772 | 0.2500 | 13.3759 |
| main-stability | 50 | 49.5 | static-balanced | 3 | 198.180 | 44.4 | 10.212 | 0.2500 | 13.3822 |
| main-stability | 50 | 49.6 | Heavy | 1 | 189.017 | 45.9 | 7.429 | 0.2500 | 13.5495 |
| main-stability | 50 | 49.7 | Heavy | 2 | 197.992 | 46.3 | 6.877 | 0.2500 | 13.5490 |
| main-stability | 50 | 49.8 | Heavy | 3 | 200.484 | 46.6 | 6.488 | 0.2500 | 13.5483 |
| main-stability | 50 | 50.0 | Lightweight | 1 | 101.214 | 47.9 | 4.167 | 0.1251 | 13.2789 |
| main-stability | 50 | 49.5 | Lightweight | 2 | 104.032 | 47.5 | 4.238 | 0.1251 | 13.2797 |
| main-stability | 50 | 49.4 | Lightweight | 3 | 101.445 | 47.7 | 3.276 | 0.1251 | 13.2763 |
| main-stability | 75 | 74.5 | Adaptive | 1 | 195.973 | 53.7 | 27.923 | 0.2243 | 13.4206 |
| main-stability | 75 | 75.0 | Adaptive | 2 | 137.498 | 52.5 | 30.044 | 0.2257 | 13.4227 |
| main-stability | 75 | 73.6 | Adaptive | 3 | 141.028 | 56.6 | 23.143 | 0.2269 | 13.4129 |
| main-stability | 75 | 74.3 | static-balanced | 1 | 101.597 | 63.0 | 15.141 | 0.2500 | 13.3598 |
| main-stability | 75 | 73.6 | static-balanced | 2 | 198.935 | 54.1 | 26.443 | 0.2500 | 13.3674 |
| main-stability | 75 | 71.1 | static-balanced | 3 | 101.383 | 50.3 | 29.208 | 0.2500 | 13.3751 |
| main-stability | 75 | 75.0 | Heavy | 1 | 102.426 | 56.7 | 24.356 | 0.2500 | 13.5343 |
| main-stability | 75 | 75.0 | Heavy | 2 | 199.089 | 56.1 | 25.195 | 0.2500 | 13.5351 |
| main-stability | 75 | 75.0 | Heavy | 3 | 198.307 | 56.7 | 24.350 | 0.2500 | 13.5342 |
| main-stability | 75 | 74.0 | Lightweight | 1 | 101.417 | 56.3 | 23.885 | 0.1251 | 13.2670 |
| main-stability | 75 | 73.1 | Lightweight | 2 | 101.698 | 57.2 | 21.774 | 0.1251 | 13.2637 |
| main-stability | 75 | 75.0 | Lightweight | 3 | 168.912 | 57.4 | 23.489 | 0.1251 | 13.2635 |
| main-stability | 100 | 100.0 | Adaptive | 1 | 195.813 | 61.2 | 38.783 | 0.2243 | 13.4078 |
| main-stability | 100 | 97.8 | Adaptive | 2 | 168.378 | 58.6 | 40.068 | 0.2256 | 13.4087 |
| main-stability | 100 | 99.1 | Adaptive | 3 | 195.263 | 61.3 | 38.120 | 0.2265 | 13.4085 |
| main-stability | 100 | 97.2 | static-balanced | 1 | 100.878 | 59.8 | 38.484 | 0.2500 | 13.3632 |
| main-stability | 100 | 98.7 | static-balanced | 2 | 102.750 | 64.5 | 34.662 | 0.2500 | 13.3585 |
| main-stability | 100 | 100.0 | static-balanced | 3 | 115.387 | 59.9 | 40.083 | 0.2500 | 13.3608 |
| main-stability | 100 | 99.8 | Heavy | 1 | 133.859 | 59.8 | 40.110 | 0.2500 | 13.5311 |
| main-stability | 100 | 99.6 | Heavy | 2 | 100.326 | 58.4 | 41.425 | 0.2500 | 13.5325 |
| main-stability | 100 | 94.5 | Heavy | 3 | 124.843 | 58.4 | 38.194 | 0.2500 | 13.5301 |
| main-stability | 100 | 98.2 | Lightweight | 1 | 195.881 | 58.4 | 40.536 | 0.1251 | 13.2601 |
| main-stability | 100 | 98.2 | Lightweight | 2 | 128.887 | 62.7 | 36.206 | 0.1251 | 13.2580 |
| main-stability | 100 | 98.3 | Lightweight | 3 | 101.543 | 63.1 | 35.832 | 0.1251 | 13.2578 |
| main-stability | 150 | 141.1 | Adaptive | 1 | 103.044 | 58.7 | 58.410 | 0.2198 | 13.4083 |
| main-stability | 150 | 138.4 | Adaptive | 2 | 197.531 | 56.2 | 59.359 | 0.2221 | 13.4079 |
| main-stability | 150 | 148.3 | Adaptive | 3 | 101.289 | 65.2 | 56.064 | 0.2235 | 13.4056 |
| main-stability | 150 | 147.8 | static-balanced | 1 | 101.890 | 68.0 | 54.019 | 0.2500 | 13.3535 |
| main-stability | 150 | 150.0 | static-balanced | 2 | 196.844 | 68.7 | 54.189 | 0.2500 | 13.3490 |
| main-stability | 150 | 149.6 | static-balanced | 3 | 199.749 | 60.1 | 59.811 | 0.2500 | 13.3584 |
| main-stability | 150 | 145.8 | Heavy | 1 | 102.715 | 67.0 | 54.025 | 0.2500 | 13.5225 |
| main-stability | 150 | 147.6 | Heavy | 2 | 105.226 | 67.0 | 54.573 | 0.2500 | 13.5244 |
| main-stability | 150 | 146.8 | Heavy | 3 | 100.948 | 71.8 | 51.073 | 0.2500 | 13.5206 |
| main-stability | 150 | 148.6 | Lightweight | 1 | 199.649 | 58.8 | 60.453 | 0.1251 | 13.2599 |
| main-stability | 150 | 141.8 | Lightweight | 2 | 239.077 | 56.5 | 60.181 | 0.1251 | 13.2647 |
| main-stability | 150 | 141.0 | Lightweight | 3 | 201.109 | 56.2 | 60.142 | 0.1251 | 13.2626 |
| main-stability | 200 | 197.3 | Adaptive | 1 | 200.354 | 59.6 | 69.764 | 0.2253 | 13.4084 |
| main-stability | 200 | 195.7 | Adaptive | 2 | 197.658 | 60.0 | 69.318 | 0.2243 | 13.4120 |
| main-stability | 200 | 195.8 | Adaptive | 3 | 199.721 | 58.1 | 70.305 | 0.2237 | 13.4100 |
| main-stability | 200 | 189.2 | static-balanced | 1 | 197.403 | 61.2 | 67.627 | 0.2500 | 13.3595 |
| main-stability | 200 | 196.5 | static-balanced | 2 | 201.448 | 59.2 | 69.859 | 0.2500 | 13.3594 |
| main-stability | 200 | 190.6 | static-balanced | 3 | 295.426 | 61.7 | 67.605 | 0.2500 | 13.3547 |
| main-stability | 200 | 193.6 | Heavy | 1 | 200.797 | 60.4 | 68.810 | 0.2500 | 13.5259 |
| main-stability | 200 | 195.3 | Heavy | 2 | 198.576 | 62.9 | 67.813 | 0.2500 | 13.5280 |
| main-stability | 200 | 194.2 | Heavy | 3 | 200.913 | 60.9 | 68.615 | 0.2500 | 13.5276 |
| main-stability | 200 | 197.3 | Lightweight | 1 | 200.444 | 61.4 | 68.871 | 0.1251 | 13.2572 |
| main-stability | 200 | 198.3 | Lightweight | 2 | 198.301 | 63.9 | 67.776 | 0.1251 | 13.2550 |
| main-stability | 200 | 194.8 | Lightweight | 3 | 198.154 | 65.8 | 66.196 | 0.1251 | 13.2553 |
| main-stability | 300 | 279.1 | Adaptive | 1 | 297.266 | 66.0 | 76.373 | 0.2238 | 13.3911 |
| main-stability | 300 | 300.0 | Adaptive | 2 | 199.256 | 60.8 | 79.732 | 0.2225 | 13.3969 |
| main-stability | 300 | 295.6 | Adaptive | 3 | 199.019 | 63.7 | 78.447 | 0.2230 | 13.4009 |
| main-stability | 300 | 298.9 | static-balanced | 1 | 198.392 | 63.1 | 78.873 | 0.2500 | 13.3577 |
| main-stability | 300 | 295.4 | static-balanced | 2 | 200.512 | 62.3 | 78.918 | 0.2500 | 13.3564 |
| main-stability | 300 | 291.4 | static-balanced | 3 | 200.033 | 64.0 | 78.040 | 0.2500 | 13.3549 |
| main-stability | 300 | 256.4 | Heavy | 1 | 198.630 | 61.4 | 76.048 | 0.2500 | 13.5272 |
| main-stability | 300 | 295.1 | Heavy | 2 | 298.456 | 63.5 | 78.467 | 0.2500 | 13.5232 |
| main-stability | 300 | 277.0 | Heavy | 3 | 198.603 | 62.0 | 77.631 | 0.2500 | 13.5267 |
| main-stability | 300 | 289.7 | Lightweight | 1 | 198.126 | 61.0 | 78.952 | 0.1251 | 13.2576 |
| main-stability | 300 | 255.3 | Lightweight | 2 | 197.219 | 63.0 | 75.341 | 0.1251 | 13.2580 |
| main-stability | 300 | 220.3 | Lightweight | 3 | 199.216 | 59.2 | 73.141 | 0.1251 | 13.2572 |
| network-impairment | 100 | 97.3 | Adaptive | 1 | 295.646 | 54.5 | 44.068 | 0.2231 | 13.4054 |
| network-impairment | 100 | 89.8 | Adaptive | 1 | 2863.309 | 7.6 | 91.517 | 0.2243 | 13.5411 |
| network-impairment | 100 | 37.8 | Adaptive | 1 | 1045.680 | 2.1 | 94.312 | 0.2067 | 11.1358 |
| network-impairment | 100 | 98.4 | Adaptive | 2 | 200.773 | 56.6 | 42.477 | 0.2245 | 13.4092 |
| network-impairment | 100 | 99.9 | Adaptive | 2 | 1641.189 | 10.2 | 89.793 | 0.2225 | 13.4597 |
| network-impairment | 100 | 3.2 | Adaptive | 2 | 3423.393 | 0.5 | 85.128 | 0.2132 | 11.4156 |
| network-impairment | 100 | 98.0 | Adaptive | 3 | 197.325 | 54.6 | 44.312 | 0.2239 | 13.4100 |
| network-impairment | 100 | 100.0 | Adaptive | 3 | 1610.322 | 10.6 | 89.383 | 0.2325 | 13.4772 |
| network-impairment | 100 | 7.4 | Adaptive | 3 | 624.722 | 1.8 | 75.566 | 0.2126 | 11.3945 |
| network-impairment | 100 | 99.5 | static-balanced | 1 | 295.301 | 52.2 | 47.581 | 0.2500 | 13.3674 |
| network-impairment | 100 | 92.7 | static-balanced | 1 | 1705.948 | 10.6 | 88.523 | 0.2500 | 13.4506 |
| network-impairment | 100 | 9.6 | static-balanced | 1 | 978.862 | 1.8 | 80.936 | 0.2183 | 11.6985 |
| network-impairment | 100 | 96.2 | static-balanced | 2 | 196.494 | 53.0 | 44.835 | 0.2500 | 13.3689 |
| network-impairment | 100 | 100.0 | static-balanced | 2 | 1495.308 | 12.0 | 88.017 | 0.2500 | 13.4339 |
| network-impairment | 100 | 93.6 | static-balanced | 2 | 2034.417 | 0.3 | 99.662 | 0.2500 | 15.6379 |
| network-impairment | 100 | 98.8 | static-balanced | 3 | 200.178 | 51.0 | 48.313 | 0.2500 | 13.3715 |
| network-impairment | 100 | 91.7 | static-balanced | 3 | 2812.750 | 8.0 | 91.277 | 0.2500 | 13.4993 |
| network-impairment | 100 | 97.5 | static-balanced | 3 | 2219.775 | 0.5 | 99.470 | 0.2348 | 13.8322 |
| network-impairment | 100 | 100.0 | Heavy | 1 | 199.194 | 57.4 | 42.650 | 0.2500 | 13.5336 |
| network-impairment | 100 | 99.3 | Heavy | 1 | 2022.805 | 10.0 | 89.894 | 0.2500 | 13.6439 |
| network-impairment | 100 | 27.7 | Heavy | 1 | 845.582 | 2.9 | 89.483 | 0.2303 | 12.5095 |
| network-impairment | 100 | 97.0 | Heavy | 2 | 199.173 | 54.4 | 43.908 | 0.2500 | 13.5372 |
| network-impairment | 100 | 98.3 | Heavy | 2 | 1334.413 | 11.9 | 87.907 | 0.2500 | 13.6051 |
| network-impairment | 100 | 29.7 | Heavy | 2 | 2387.132 | 0.7 | 97.532 | 0.1897 | 10.4116 |
| network-impairment | 100 | 96.7 | Heavy | 3 | 103.310 | 56.5 | 41.547 | 0.2500 | 13.5368 |
| network-impairment | 100 | 94.5 | Heavy | 3 | 1575.028 | 11.9 | 87.361 | 0.2500 | 13.6160 |
| network-impairment | 100 | 36.9 | Heavy | 3 | 2525.011 | 1.1 | 96.924 | 0.2267 | 12.4790 |
| network-impairment | 100 | 99.0 | Lightweight | 1 | 201.536 | 50.9 | 48.637 | 0.1251 | 13.2692 |
| network-impairment | 100 | 99.3 | Lightweight | 1 | 1195.236 | 13.9 | 85.990 | 0.1251 | 13.3350 |
| network-impairment | 100 | 10.6 | Lightweight | 1 | 1000.831 | 1.6 | 84.953 | 0.1133 | 12.0582 |
| network-impairment | 100 | 98.5 | Lightweight | 2 | 200.190 | 49.9 | 49.366 | 0.1251 | 13.2733 |
| network-impairment | 100 | 96.7 | Lightweight | 2 | 1729.719 | 10.2 | 89.402 | 0.1251 | 13.3555 |
| network-impairment | 100 | 14.9 | Lightweight | 2 | 632.490 | 3.3 | 77.790 | 0.1180 | 12.5407 |
| network-impairment | 100 | 99.8 | Lightweight | 3 | 202.011 | 53.0 | 46.902 | 0.1251 | 13.2690 |
| network-impairment | 100 | 98.5 | Lightweight | 3 | 1152.696 | 14.3 | 85.480 | 0.1251 | 13.3314 |
| network-impairment | 100 | 88.6 | Lightweight | 3 | 1089.159 | 0.3 | 99.662 | 0.1251 | 15.6365 |
| rekey-sensitivity | 100 | 98.2 | Adaptive | 1 | 297.744 | 60.8 | 38.151 | 0.2241 | 13.4021 |
| rekey-sensitivity | 100 | 99.8 | Adaptive | 1 | 300.198 | 58.7 | 41.192 | 0.2237 | 13.3780 |
| rekey-sensitivity | 100 | 99.2 | Adaptive | 1 | 203.617 | 55.9 | 43.654 | 0.2237 | 13.3615 |
| rekey-sensitivity | 100 | 99.5 | Adaptive | 2 | 201.078 | 56.0 | 43.780 | 0.2239 | 13.4142 |
| rekey-sensitivity | 100 | 96.0 | Adaptive | 2 | 200.346 | 55.4 | 42.277 | 0.2224 | 13.3726 |
| rekey-sensitivity | 100 | 95.7 | Adaptive | 2 | 105.244 | 59.4 | 37.918 | 0.2232 | 13.3575 |
| rekey-sensitivity | 100 | 99.0 | Adaptive | 3 | 200.824 | 63.7 | 35.640 | 0.2232 | 13.4060 |
| rekey-sensitivity | 100 | 99.3 | Adaptive | 3 | 198.428 | 56.1 | 43.469 | 0.2277 | 13.3851 |
| rekey-sensitivity | 100 | 96.9 | Adaptive | 3 | 201.683 | 54.7 | 43.604 | 0.2255 | 13.3677 |
| rekey-sensitivity | 100 | 99.6 | static-balanced | 1 | 201.038 | 64.5 | 35.274 | 0.2500 | 13.3565 |
| rekey-sensitivity | 100 | 100.0 | static-balanced | 1 | 300.556 | 55.5 | 44.500 | 0.2500 | 13.3297 |
| rekey-sensitivity | 100 | 98.7 | static-balanced | 1 | 204.749 | 54.9 | 44.334 | 0.2500 | 13.3155 |
| rekey-sensitivity | 100 | 100.0 | static-balanced | 2 | 199.825 | 63.0 | 36.983 | 0.2500 | 13.3578 |
| rekey-sensitivity | 100 | 100.0 | static-balanced | 2 | 198.582 | 55.8 | 44.167 | 0.2500 | 13.3296 |
| rekey-sensitivity | 100 | 98.5 | static-balanced | 2 | 296.217 | 54.3 | 44.901 | 0.2500 | 13.3157 |
| rekey-sensitivity | 100 | 100.0 | static-balanced | 3 | 264.831 | 59.7 | 40.257 | 0.2500 | 13.3588 |
| rekey-sensitivity | 100 | 97.3 | static-balanced | 3 | 201.605 | 55.5 | 43.031 | 0.2500 | 13.3298 |
| rekey-sensitivity | 100 | 99.8 | static-balanced | 3 | 196.602 | 57.8 | 42.038 | 0.2500 | 13.3146 |
| rekey-sensitivity | 100 | 99.1 | Heavy | 1 | 298.165 | 64.1 | 35.346 | 0.2500 | 13.5268 |
| rekey-sensitivity | 100 | 98.9 | Heavy | 1 | 198.880 | 62.6 | 36.731 | 0.2500 | 13.4963 |
| rekey-sensitivity | 100 | 96.9 | Heavy | 1 | 201.626 | 54.4 | 43.858 | 0.2500 | 13.4856 |
| rekey-sensitivity | 100 | 98.8 | Heavy | 2 | 197.556 | 59.9 | 39.325 | 0.2500 | 13.5309 |
| rekey-sensitivity | 100 | 98.7 | Heavy | 2 | 120.811 | 64.3 | 34.909 | 0.2500 | 13.4956 |
| rekey-sensitivity | 100 | 99.7 | Heavy | 2 | 360.768 | 53.0 | 46.833 | 0.2500 | 13.4862 |
| rekey-sensitivity | 100 | 99.4 | Heavy | 3 | 200.406 | 60.0 | 39.661 | 0.2500 | 13.5309 |
| rekey-sensitivity | 100 | 100.0 | Heavy | 3 | 103.065 | 60.1 | 39.850 | 0.2500 | 13.4973 |
| rekey-sensitivity | 100 | 99.1 | Heavy | 3 | 293.734 | 58.4 | 41.073 | 0.2500 | 13.4846 |
| rekey-sensitivity | 100 | 99.7 | Lightweight | 1 | 199.882 | 60.9 | 38.920 | 0.1251 | 13.2599 |
| rekey-sensitivity | 100 | 98.8 | Lightweight | 1 | 295.891 | 56.5 | 42.768 | 0.1251 | 13.2292 |
| rekey-sensitivity | 100 | 95.3 | Lightweight | 1 | 199.739 | 55.4 | 41.863 | 0.1251 | 13.2154 |
| rekey-sensitivity | 100 | 100.0 | Lightweight | 2 | 249.137 | 62.2 | 37.833 | 0.1251 | 13.2587 |
| rekey-sensitivity | 100 | 98.3 | Lightweight | 2 | 265.201 | 54.0 | 45.060 | 0.1251 | 13.2306 |
| rekey-sensitivity | 100 | 96.7 | Lightweight | 2 | 200.795 | 54.8 | 43.357 | 0.1251 | 13.2156 |
| rekey-sensitivity | 100 | 100.0 | Lightweight | 3 | 199.002 | 63.3 | 36.700 | 0.1251 | 13.2576 |
| rekey-sensitivity | 100 | 95.9 | Lightweight | 3 | 199.748 | 55.4 | 42.256 | 0.1251 | 13.2298 |
| rekey-sensitivity | 100 | 100.0 | Lightweight | 3 | 198.430 | 56.0 | 44.000 | 0.1251 | 13.2152 |

## Mode Averages

## CPU Sensitivity

| Parameter | Offered rate | Mode | Runs | Median throughput | Median drop % | Mean throughput | Throughput std | Median crypto work (MiB/msg) | Median energy/msg |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.05 | 100 | Adaptive | 3 | 54.2 | 43.926 | 55.5 | 3.90 | 0.2233 | 13.4066 |
| 0.05 | 100 | static-balanced | 3 | 57.3 | 41.428 | 57.2 | 4.06 | 0.2500 | 13.3613 |
| 0.05 | 100 | Heavy | 3 | 53.7 | 46.056 | 53.8 | 3.34 | 0.2500 | 13.5355 |
| 0.05 | 100 | Lightweight | 3 | 53.5 | 43.768 | 54.2 | 2.56 | 0.1251 | 13.2677 |
| 0.05 | 200 | Adaptive | 3 | 76.4 | 61.585 | 72.8 | 6.60 | 0.2265 | 13.3908 |
| 0.05 | 200 | static-balanced | 3 | 65.7 | 66.832 | 65.8 | 2.24 | 0.2500 | 13.3554 |
| 0.05 | 200 | Heavy | 3 | 60.5 | 68.860 | 60.1 | 2.62 | 0.2500 | 13.5304 |
| 0.05 | 200 | Lightweight | 3 | 69.8 | 64.612 | 70.1 | 0.82 | 0.1251 | 13.2506 |
| 0.1 | 100 | Adaptive | 3 | 99.9 | 0.117 | 99.8 | 0.08 | 0.2250 | 13.3900 |
| 0.1 | 100 | static-balanced | 3 | 100.0 | 0.000 | 99.9 | 0.06 | 0.2500 | 13.3421 |
| 0.1 | 100 | Heavy | 3 | 99.9 | 0.000 | 99.9 | 0.09 | 0.2500 | 13.5109 |
| 0.1 | 100 | Lightweight | 3 | 100.0 | 0.000 | 100.0 | 0.01 | 0.1251 | 13.2421 |
| 0.1 | 200 | Adaptive | 3 | 155.4 | 21.873 | 153.2 | 4.18 | 0.2252 | 13.3743 |
| 0.1 | 200 | static-balanced | 3 | 151.9 | 23.930 | 152.2 | 0.94 | 0.2500 | 13.3267 |
| 0.1 | 200 | Heavy | 3 | 147.7 | 26.002 | 147.6 | 0.74 | 0.2500 | 13.4976 |
| 0.1 | 200 | Lightweight | 3 | 151.2 | 24.204 | 150.7 | 2.77 | 0.1251 | 13.2269 |
| 0.25 | 100 | Adaptive | 3 | 100.0 | 0.000 | 100.0 | 0.00 | 0.2250 | 13.3927 |
| 0.25 | 100 | static-balanced | 3 | 100.0 | 0.000 | 100.0 | 0.00 | 0.2500 | 13.3449 |
| 0.25 | 100 | Heavy | 3 | 100.0 | 0.000 | 100.0 | 0.00 | 0.2500 | 13.5147 |
| 0.25 | 100 | Lightweight | 3 | 100.0 | 0.000 | 100.0 | 0.00 | 0.1251 | 13.2448 |
| 0.25 | 200 | Adaptive | 3 | 200.0 | 0.000 | 199.7 | 0.54 | 0.2250 | 13.3704 |
| 0.25 | 200 | static-balanced | 3 | 200.0 | 0.000 | 200.0 | 0.00 | 0.2500 | 13.3225 |
| 0.25 | 200 | Heavy | 3 | 200.0 | 0.000 | 200.0 | 0.00 | 0.2500 | 13.4922 |
| 0.25 | 200 | Lightweight | 3 | 200.0 | 0.000 | 200.0 | 0.00 | 0.1251 | 13.2225 |

## Rekey Sensitivity

| Parameter | Offered rate | Mode | Runs | Median throughput | Median drop % | Mean throughput | Throughput std | Median crypto work (MiB/msg) | Median energy/msg |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10.0 | 100 | Adaptive | 3 | 55.9 | 43.604 | 56.7 | 2.48 | 0.2237 | 13.3615 |
| 10.0 | 100 | static-balanced | 3 | 54.9 | 44.334 | 55.7 | 1.87 | 0.2500 | 13.3155 |
| 10.0 | 100 | Heavy | 3 | 54.4 | 43.858 | 55.3 | 2.81 | 0.2500 | 13.4856 |
| 10.0 | 100 | Lightweight | 3 | 55.4 | 43.357 | 55.4 | 0.61 | 0.1251 | 13.2154 |
| 2.0 | 100 | Adaptive | 3 | 60.8 | 38.151 | 60.2 | 3.91 | 0.2239 | 13.4060 |
| 2.0 | 100 | static-balanced | 3 | 63.0 | 36.983 | 62.4 | 2.43 | 0.2500 | 13.3578 |
| 2.0 | 100 | Heavy | 3 | 60.0 | 39.325 | 61.3 | 2.39 | 0.2500 | 13.5309 |
| 2.0 | 100 | Lightweight | 3 | 62.2 | 37.833 | 62.1 | 1.22 | 0.1251 | 13.2587 |
| 5.0 | 100 | Adaptive | 3 | 56.1 | 42.277 | 56.8 | 1.72 | 0.2237 | 13.3780 |
| 5.0 | 100 | static-balanced | 3 | 55.5 | 44.167 | 55.6 | 0.21 | 0.2500 | 13.3297 |
| 5.0 | 100 | Heavy | 3 | 62.6 | 36.731 | 62.3 | 2.07 | 0.2500 | 13.4963 |
| 5.0 | 100 | Lightweight | 3 | 55.4 | 42.768 | 55.3 | 1.24 | 0.1251 | 13.2298 |

## Network Impairment

| Parameter | Offered rate | Mode | Runs | Median throughput | Median drop % | Mean throughput | Throughput std | Median crypto work (MiB/msg) | Median energy/msg |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| clean | 100 | Adaptive | 3 | 54.6 | 44.068 | 55.2 | 1.19 | 0.2239 | 13.4092 |
| clean | 100 | static-balanced | 3 | 52.2 | 47.581 | 52.1 | 1.00 | 0.2500 | 13.3689 |
| clean | 100 | Heavy | 3 | 56.5 | 42.650 | 56.1 | 1.52 | 0.2500 | 13.5368 |
| clean | 100 | Lightweight | 3 | 50.9 | 48.637 | 51.2 | 1.58 | 0.1251 | 13.2692 |
| lossy | 100 | Adaptive | 3 | 1.8 | 85.128 | 1.5 | 0.88 | 0.2126 | 11.3945 |
| lossy | 100 | static-balanced | 3 | 0.5 | 99.470 | 0.9 | 0.82 | 0.2348 | 13.8322 |
| lossy | 100 | Heavy | 3 | 1.1 | 96.924 | 1.6 | 1.16 | 0.2267 | 12.4790 |
| lossy | 100 | Lightweight | 3 | 1.6 | 84.953 | 1.7 | 1.51 | 0.1180 | 12.5407 |
| mild | 100 | Adaptive | 3 | 10.2 | 89.793 | 9.5 | 1.63 | 0.2243 | 13.4772 |
| mild | 100 | static-balanced | 3 | 10.6 | 88.523 | 10.2 | 2.03 | 0.2500 | 13.4506 |
| mild | 100 | Heavy | 3 | 11.9 | 87.907 | 11.3 | 1.09 | 0.2500 | 13.6160 |
| mild | 100 | Lightweight | 3 | 13.9 | 85.990 | 12.8 | 2.24 | 0.1251 | 13.3350 |

| Mode | Avg P50 latency (ms) | Avg throughput (msg/s) | Avg crypto work (MiB/msg) | Avg energy / delivered message |
| --- | ---: | ---: | ---: | ---: |
| Heavy | 317.346 | 67.8 | 0.2482 | 13.4403 |
| Adaptive | 327.292 | 67.8 | 0.2237 | 13.2981 |
| Lightweight | 242.932 | 67.7 | 0.1248 | 13.2692 |

## Selected Runs

| Offered rate | Mode | Run directory |
| ---: | --- | --- |
| 25 | Adaptive | `20260524-011559-saturation-adaptive-long-main-stability-adaptive-25hz-cpu0p05-rekey2p0-clean-r1` |
| 25 | Adaptive | `20260524-011730-saturation-adaptive-long-main-stability-adaptive-25hz-cpu0p05-rekey2p0-clean-r2` |
| 25 | Adaptive | `20260524-011900-saturation-adaptive-long-main-stability-adaptive-25hz-cpu0p05-rekey2p0-clean-r3` |
| 25 | static-balanced | `20260524-010702-saturation-adaptive-long-main-stability-static-balanced-25hz-cpu0p05-rekey2p0-clean-r1` |
| 25 | static-balanced | `20260524-010831-saturation-adaptive-long-main-stability-static-balanced-25hz-cpu0p05-rekey2p0-clean-r2` |
| 25 | static-balanced | `20260524-011001-saturation-adaptive-long-main-stability-static-balanced-25hz-cpu0p05-rekey2p0-clean-r3` |
| 25 | Heavy | `20260524-010231-saturation-adaptive-long-main-stability-static-heavy-25hz-cpu0p05-rekey2p0-clean-r1` |
| 25 | Heavy | `20260524-010401-saturation-adaptive-long-main-stability-static-heavy-25hz-cpu0p05-rekey2p0-clean-r2` |
| 25 | Heavy | `20260524-010531-saturation-adaptive-long-main-stability-static-heavy-25hz-cpu0p05-rekey2p0-clean-r3` |
| 25 | Lightweight | `20260524-011130-saturation-adaptive-long-main-stability-static-lightweight-25hz-cpu0p05-rekey2p0-clean-r1` |
| 25 | Lightweight | `20260524-011302-saturation-adaptive-long-main-stability-static-lightweight-25hz-cpu0p05-rekey2p0-clean-r2` |
| 25 | Lightweight | `20260524-011430-saturation-adaptive-long-main-stability-static-lightweight-25hz-cpu0p05-rekey2p0-clean-r3` |
| 50 | Adaptive | `20260524-013350-saturation-adaptive-long-main-stability-adaptive-50hz-cpu0p05-rekey2p0-clean-r1` |
| 50 | Adaptive | `20260524-013516-saturation-adaptive-long-main-stability-adaptive-50hz-cpu0p05-rekey2p0-clean-r2` |
| 50 | Adaptive | `20260524-013645-saturation-adaptive-long-main-stability-adaptive-50hz-cpu0p05-rekey2p0-clean-r3` |
| 50 | static-balanced | `20260524-012500-saturation-adaptive-long-main-stability-static-balanced-50hz-cpu0p05-rekey2p0-clean-r1` |
| 50 | static-balanced | `20260524-012633-saturation-adaptive-long-main-stability-static-balanced-50hz-cpu0p05-rekey2p0-clean-r2` |
| 50 | static-balanced | `20260524-012802-saturation-adaptive-long-main-stability-static-balanced-50hz-cpu0p05-rekey2p0-clean-r3` |
| 50 | Heavy | `20260524-012031-saturation-adaptive-long-main-stability-static-heavy-50hz-cpu0p05-rekey2p0-clean-r1` |
| 50 | Heavy | `20260524-012203-saturation-adaptive-long-main-stability-static-heavy-50hz-cpu0p05-rekey2p0-clean-r2` |
| 50 | Heavy | `20260524-012330-saturation-adaptive-long-main-stability-static-heavy-50hz-cpu0p05-rekey2p0-clean-r3` |
| 50 | Lightweight | `20260524-012930-saturation-adaptive-long-main-stability-static-lightweight-50hz-cpu0p05-rekey2p0-clean-r1` |
| 50 | Lightweight | `20260524-013058-saturation-adaptive-long-main-stability-static-lightweight-50hz-cpu0p05-rekey2p0-clean-r2` |
| 50 | Lightweight | `20260524-013225-saturation-adaptive-long-main-stability-static-lightweight-50hz-cpu0p05-rekey2p0-clean-r3` |
| 75 | Adaptive | `20260524-015137-saturation-adaptive-long-main-stability-adaptive-75hz-cpu0p05-rekey2p0-clean-r1` |
| 75 | Adaptive | `20260524-015304-saturation-adaptive-long-main-stability-adaptive-75hz-cpu0p05-rekey2p0-clean-r2` |
| 75 | Adaptive | `20260524-015428-saturation-adaptive-long-main-stability-adaptive-75hz-cpu0p05-rekey2p0-clean-r3` |
| 75 | static-balanced | `20260524-014242-saturation-adaptive-long-main-stability-static-balanced-75hz-cpu0p05-rekey2p0-clean-r1` |
| 75 | static-balanced | `20260524-014411-saturation-adaptive-long-main-stability-static-balanced-75hz-cpu0p05-rekey2p0-clean-r2` |
| 75 | static-balanced | `20260524-014541-saturation-adaptive-long-main-stability-static-balanced-75hz-cpu0p05-rekey2p0-clean-r3` |
| 75 | Heavy | `20260524-013815-saturation-adaptive-long-main-stability-static-heavy-75hz-cpu0p05-rekey2p0-clean-r1` |
| 75 | Heavy | `20260524-013944-saturation-adaptive-long-main-stability-static-heavy-75hz-cpu0p05-rekey2p0-clean-r2` |
| 75 | Heavy | `20260524-014114-saturation-adaptive-long-main-stability-static-heavy-75hz-cpu0p05-rekey2p0-clean-r3` |
| 75 | Lightweight | `20260524-014711-saturation-adaptive-long-main-stability-static-lightweight-75hz-cpu0p05-rekey2p0-clean-r1` |
| 75 | Lightweight | `20260524-014840-saturation-adaptive-long-main-stability-static-lightweight-75hz-cpu0p05-rekey2p0-clean-r2` |
| 75 | Lightweight | `20260524-015010-saturation-adaptive-long-main-stability-static-lightweight-75hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Adaptive | `20260524-020901-saturation-adaptive-long-main-stability-adaptive-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Adaptive | `20260524-021028-saturation-adaptive-long-main-stability-adaptive-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Adaptive | `20260524-021157-saturation-adaptive-long-main-stability-adaptive-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Adaptive | `20260524-032104-saturation-adaptive-long-cpu-sensitivity-adaptive-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Adaptive | `20260524-032239-saturation-adaptive-long-cpu-sensitivity-adaptive-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Adaptive | `20260524-032413-saturation-adaptive-long-cpu-sensitivity-adaptive-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Adaptive | `20260524-035433-saturation-adaptive-long-cpu-sensitivity-adaptive-100hz-cpu0p1-rekey2p0-clean-r1` |
| 100 | Adaptive | `20260524-035546-saturation-adaptive-long-cpu-sensitivity-adaptive-100hz-cpu0p1-rekey2p0-clean-r2` |
| 100 | Adaptive | `20260524-035701-saturation-adaptive-long-cpu-sensitivity-adaptive-100hz-cpu0p1-rekey2p0-clean-r3` |
| 100 | Adaptive | `20260524-042239-saturation-adaptive-long-cpu-sensitivity-adaptive-100hz-cpu0p25-rekey2p0-clean-r1` |
| 100 | Adaptive | `20260524-042343-saturation-adaptive-long-cpu-sensitivity-adaptive-100hz-cpu0p25-rekey2p0-clean-r2` |
| 100 | Adaptive | `20260524-042450-saturation-adaptive-long-cpu-sensitivity-adaptive-100hz-cpu0p25-rekey2p0-clean-r3` |
| 100 | Adaptive | `20260524-045214-saturation-adaptive-long-rekey-sensitivity-adaptive-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Adaptive | `20260524-045344-saturation-adaptive-long-rekey-sensitivity-adaptive-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Adaptive | `20260524-045515-saturation-adaptive-long-rekey-sensitivity-adaptive-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Adaptive | `20260524-051021-saturation-adaptive-long-rekey-sensitivity-adaptive-100hz-cpu0p05-rekey5p0-clean-r1` |
| 100 | Adaptive | `20260524-051149-saturation-adaptive-long-rekey-sensitivity-adaptive-100hz-cpu0p05-rekey5p0-clean-r2` |
| 100 | Adaptive | `20260524-051319-saturation-adaptive-long-rekey-sensitivity-adaptive-100hz-cpu0p05-rekey5p0-clean-r3` |
| 100 | Adaptive | `20260524-052825-saturation-adaptive-long-rekey-sensitivity-adaptive-100hz-cpu0p05-rekey10p0-clean-r1` |
| 100 | Adaptive | `20260524-052956-saturation-adaptive-long-rekey-sensitivity-adaptive-100hz-cpu0p05-rekey10p0-clean-r2` |
| 100 | Adaptive | `20260524-053126-saturation-adaptive-long-rekey-sensitivity-adaptive-100hz-cpu0p05-rekey10p0-clean-r3` |
| 100 | Adaptive | `20260524-062318-saturation-adaptive-long-network-impairment-adaptive-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Adaptive | `20260524-062448-saturation-adaptive-long-network-impairment-adaptive-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Adaptive | `20260524-062617-saturation-adaptive-long-network-impairment-adaptive-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Adaptive | `20260524-062746-saturation-adaptive-long-network-impairment-adaptive-100hz-cpu0p05-rekey2p0-mild-r1` |
| 100 | Adaptive | `20260524-062916-saturation-adaptive-long-network-impairment-adaptive-100hz-cpu0p05-rekey2p0-mild-r2` |
| 100 | Adaptive | `20260524-063050-saturation-adaptive-long-network-impairment-adaptive-100hz-cpu0p05-rekey2p0-mild-r3` |
| 100 | Adaptive | `20260524-063226-saturation-adaptive-long-network-impairment-adaptive-100hz-cpu0p05-rekey2p0-lossy-r1` |
| 100 | Adaptive | `20260524-063459-saturation-adaptive-long-network-impairment-adaptive-100hz-cpu0p05-rekey2p0-lossy-r2` |
| 100 | Adaptive | `20260524-063729-saturation-adaptive-long-network-impairment-adaptive-100hz-cpu0p05-rekey2p0-lossy-r3` |
| 100 | static-balanced | `20260524-020021-saturation-adaptive-long-main-stability-static-balanced-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | static-balanced | `20260524-020148-saturation-adaptive-long-main-stability-static-balanced-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | static-balanced | `20260524-020315-saturation-adaptive-long-main-stability-static-balanced-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | static-balanced | `20260524-031202-saturation-adaptive-long-cpu-sensitivity-static-balanced-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | static-balanced | `20260524-031332-saturation-adaptive-long-cpu-sensitivity-static-balanced-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | static-balanced | `20260524-031500-saturation-adaptive-long-cpu-sensitivity-static-balanced-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | static-balanced | `20260524-034717-saturation-adaptive-long-cpu-sensitivity-static-balanced-100hz-cpu0p1-rekey2p0-clean-r1` |
| 100 | static-balanced | `20260524-034828-saturation-adaptive-long-cpu-sensitivity-static-balanced-100hz-cpu0p1-rekey2p0-clean-r2` |
| 100 | static-balanced | `20260524-034941-saturation-adaptive-long-cpu-sensitivity-static-balanced-100hz-cpu0p1-rekey2p0-clean-r3` |
| 100 | static-balanced | `20260524-041608-saturation-adaptive-long-cpu-sensitivity-static-balanced-100hz-cpu0p25-rekey2p0-clean-r1` |
| 100 | static-balanced | `20260524-041712-saturation-adaptive-long-cpu-sensitivity-static-balanced-100hz-cpu0p25-rekey2p0-clean-r2` |
| 100 | static-balanced | `20260524-041816-saturation-adaptive-long-cpu-sensitivity-static-balanced-100hz-cpu0p25-rekey2p0-clean-r3` |
| 100 | static-balanced | `20260524-044317-saturation-adaptive-long-rekey-sensitivity-static-balanced-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | static-balanced | `20260524-044444-saturation-adaptive-long-rekey-sensitivity-static-balanced-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | static-balanced | `20260524-044612-saturation-adaptive-long-rekey-sensitivity-static-balanced-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | static-balanced | `20260524-050116-saturation-adaptive-long-rekey-sensitivity-static-balanced-100hz-cpu0p05-rekey5p0-clean-r1` |
| 100 | static-balanced | `20260524-050244-saturation-adaptive-long-rekey-sensitivity-static-balanced-100hz-cpu0p05-rekey5p0-clean-r2` |
| 100 | static-balanced | `20260524-050415-saturation-adaptive-long-rekey-sensitivity-static-balanced-100hz-cpu0p05-rekey5p0-clean-r3` |
| 100 | static-balanced | `20260524-051918-saturation-adaptive-long-rekey-sensitivity-static-balanced-100hz-cpu0p05-rekey10p0-clean-r1` |
| 100 | static-balanced | `20260524-052050-saturation-adaptive-long-rekey-sensitivity-static-balanced-100hz-cpu0p05-rekey10p0-clean-r2` |
| 100 | static-balanced | `20260524-052217-saturation-adaptive-long-rekey-sensitivity-static-balanced-100hz-cpu0p05-rekey10p0-clean-r3` |
| 100 | static-balanced | `20260524-054947-saturation-adaptive-long-network-impairment-static-balanced-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | static-balanced | `20260524-055116-saturation-adaptive-long-network-impairment-static-balanced-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | static-balanced | `20260524-055251-saturation-adaptive-long-network-impairment-static-balanced-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | static-balanced | `20260524-055424-saturation-adaptive-long-network-impairment-static-balanced-100hz-cpu0p05-rekey2p0-mild-r1` |
| 100 | static-balanced | `20260524-055558-saturation-adaptive-long-network-impairment-static-balanced-100hz-cpu0p05-rekey2p0-mild-r2` |
| 100 | static-balanced | `20260524-055731-saturation-adaptive-long-network-impairment-static-balanced-100hz-cpu0p05-rekey2p0-mild-r3` |
| 100 | static-balanced | `20260524-055905-saturation-adaptive-long-network-impairment-static-balanced-100hz-cpu0p05-rekey2p0-lossy-r1` |
| 100 | static-balanced | `20260524-060139-saturation-adaptive-long-network-impairment-static-balanced-100hz-cpu0p05-rekey2p0-lossy-r2` |
| 100 | static-balanced | `20260524-060321-saturation-adaptive-long-network-impairment-static-balanced-100hz-cpu0p05-rekey2p0-lossy-r3` |
| 100 | Heavy | `20260524-015555-saturation-adaptive-long-main-stability-static-heavy-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Heavy | `20260524-015726-saturation-adaptive-long-main-stability-static-heavy-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Heavy | `20260524-015853-saturation-adaptive-long-main-stability-static-heavy-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Heavy | `20260524-030728-saturation-adaptive-long-cpu-sensitivity-static-heavy-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Heavy | `20260524-030900-saturation-adaptive-long-cpu-sensitivity-static-heavy-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Heavy | `20260524-031032-saturation-adaptive-long-cpu-sensitivity-static-heavy-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Heavy | `20260524-034342-saturation-adaptive-long-cpu-sensitivity-static-heavy-100hz-cpu0p1-rekey2p0-clean-r1` |
| 100 | Heavy | `20260524-034453-saturation-adaptive-long-cpu-sensitivity-static-heavy-100hz-cpu0p1-rekey2p0-clean-r2` |
| 100 | Heavy | `20260524-034605-saturation-adaptive-long-cpu-sensitivity-static-heavy-100hz-cpu0p1-rekey2p0-clean-r3` |
| 100 | Heavy | `20260524-041250-saturation-adaptive-long-cpu-sensitivity-static-heavy-100hz-cpu0p25-rekey2p0-clean-r1` |
| 100 | Heavy | `20260524-041355-saturation-adaptive-long-cpu-sensitivity-static-heavy-100hz-cpu0p25-rekey2p0-clean-r2` |
| 100 | Heavy | `20260524-041503-saturation-adaptive-long-cpu-sensitivity-static-heavy-100hz-cpu0p25-rekey2p0-clean-r3` |
| 100 | Heavy | `20260524-043854-saturation-adaptive-long-rekey-sensitivity-static-heavy-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Heavy | `20260524-044022-saturation-adaptive-long-rekey-sensitivity-static-heavy-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Heavy | `20260524-044148-saturation-adaptive-long-rekey-sensitivity-static-heavy-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Heavy | `20260524-045645-saturation-adaptive-long-rekey-sensitivity-static-heavy-100hz-cpu0p05-rekey5p0-clean-r1` |
| 100 | Heavy | `20260524-045815-saturation-adaptive-long-rekey-sensitivity-static-heavy-100hz-cpu0p05-rekey5p0-clean-r2` |
| 100 | Heavy | `20260524-045946-saturation-adaptive-long-rekey-sensitivity-static-heavy-100hz-cpu0p05-rekey5p0-clean-r3` |
| 100 | Heavy | `20260524-051447-saturation-adaptive-long-rekey-sensitivity-static-heavy-100hz-cpu0p05-rekey10p0-clean-r1` |
| 100 | Heavy | `20260524-051617-saturation-adaptive-long-rekey-sensitivity-static-heavy-100hz-cpu0p05-rekey10p0-clean-r2` |
| 100 | Heavy | `20260524-051747-saturation-adaptive-long-rekey-sensitivity-static-heavy-100hz-cpu0p05-rekey10p0-clean-r3` |
| 100 | Heavy | `20260524-053258-saturation-adaptive-long-network-impairment-static-heavy-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Heavy | `20260524-053427-saturation-adaptive-long-network-impairment-static-heavy-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Heavy | `20260524-053600-saturation-adaptive-long-network-impairment-static-heavy-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Heavy | `20260524-053734-saturation-adaptive-long-network-impairment-static-heavy-100hz-cpu0p05-rekey2p0-mild-r1` |
| 100 | Heavy | `20260524-053909-saturation-adaptive-long-network-impairment-static-heavy-100hz-cpu0p05-rekey2p0-mild-r2` |
| 100 | Heavy | `20260524-054044-saturation-adaptive-long-network-impairment-static-heavy-100hz-cpu0p05-rekey2p0-mild-r3` |
| 100 | Heavy | `20260524-054218-saturation-adaptive-long-network-impairment-static-heavy-100hz-cpu0p05-rekey2p0-lossy-r1` |
| 100 | Heavy | `20260524-054448-saturation-adaptive-long-network-impairment-static-heavy-100hz-cpu0p05-rekey2p0-lossy-r2` |
| 100 | Heavy | `20260524-054716-saturation-adaptive-long-network-impairment-static-heavy-100hz-cpu0p05-rekey2p0-lossy-r3` |
| 100 | Lightweight | `20260524-020442-saturation-adaptive-long-main-stability-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Lightweight | `20260524-020611-saturation-adaptive-long-main-stability-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Lightweight | `20260524-020736-saturation-adaptive-long-main-stability-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Lightweight | `20260524-031631-saturation-adaptive-long-cpu-sensitivity-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Lightweight | `20260524-031804-saturation-adaptive-long-cpu-sensitivity-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Lightweight | `20260524-031935-saturation-adaptive-long-cpu-sensitivity-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Lightweight | `20260524-035056-saturation-adaptive-long-cpu-sensitivity-static-lightweight-100hz-cpu0p1-rekey2p0-clean-r1` |
| 100 | Lightweight | `20260524-035209-saturation-adaptive-long-cpu-sensitivity-static-lightweight-100hz-cpu0p1-rekey2p0-clean-r2` |
| 100 | Lightweight | `20260524-035321-saturation-adaptive-long-cpu-sensitivity-static-lightweight-100hz-cpu0p1-rekey2p0-clean-r3` |
| 100 | Lightweight | `20260524-041920-saturation-adaptive-long-cpu-sensitivity-static-lightweight-100hz-cpu0p25-rekey2p0-clean-r1` |
| 100 | Lightweight | `20260524-042026-saturation-adaptive-long-cpu-sensitivity-static-lightweight-100hz-cpu0p25-rekey2p0-clean-r2` |
| 100 | Lightweight | `20260524-042132-saturation-adaptive-long-cpu-sensitivity-static-lightweight-100hz-cpu0p25-rekey2p0-clean-r3` |
| 100 | Lightweight | `20260524-044741-saturation-adaptive-long-rekey-sensitivity-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Lightweight | `20260524-044913-saturation-adaptive-long-rekey-sensitivity-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Lightweight | `20260524-045045-saturation-adaptive-long-rekey-sensitivity-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Lightweight | `20260524-050546-saturation-adaptive-long-rekey-sensitivity-static-lightweight-100hz-cpu0p05-rekey5p0-clean-r1` |
| 100 | Lightweight | `20260524-050715-saturation-adaptive-long-rekey-sensitivity-static-lightweight-100hz-cpu0p05-rekey5p0-clean-r2` |
| 100 | Lightweight | `20260524-050847-saturation-adaptive-long-rekey-sensitivity-static-lightweight-100hz-cpu0p05-rekey5p0-clean-r3` |
| 100 | Lightweight | `20260524-052350-saturation-adaptive-long-rekey-sensitivity-static-lightweight-100hz-cpu0p05-rekey10p0-clean-r1` |
| 100 | Lightweight | `20260524-052521-saturation-adaptive-long-rekey-sensitivity-static-lightweight-100hz-cpu0p05-rekey10p0-clean-r2` |
| 100 | Lightweight | `20260524-052652-saturation-adaptive-long-rekey-sensitivity-static-lightweight-100hz-cpu0p05-rekey10p0-clean-r3` |
| 100 | Lightweight | `20260524-060505-saturation-adaptive-long-network-impairment-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r1` |
| 100 | Lightweight | `20260524-060637-saturation-adaptive-long-network-impairment-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r2` |
| 100 | Lightweight | `20260524-060809-saturation-adaptive-long-network-impairment-static-lightweight-100hz-cpu0p05-rekey2p0-clean-r3` |
| 100 | Lightweight | `20260524-061200-saturation-adaptive-long-network-impairment-static-lightweight-100hz-cpu0p05-rekey2p0-mild-r1` |
| 100 | Lightweight | `20260524-061334-saturation-adaptive-long-network-impairment-static-lightweight-100hz-cpu0p05-rekey2p0-mild-r2` |
| 100 | Lightweight | `20260524-061506-saturation-adaptive-long-network-impairment-static-lightweight-100hz-cpu0p05-rekey2p0-mild-r3` |
| 100 | Lightweight | `20260524-061638-saturation-adaptive-long-network-impairment-static-lightweight-100hz-cpu0p05-rekey2p0-lossy-r1` |
| 100 | Lightweight | `20260524-061911-saturation-adaptive-long-network-impairment-static-lightweight-100hz-cpu0p05-rekey2p0-lossy-r2` |
| 100 | Lightweight | `20260524-062141-saturation-adaptive-long-network-impairment-static-lightweight-100hz-cpu0p05-rekey2p0-lossy-r3` |
| 150 | Adaptive | `20260524-022650-saturation-adaptive-long-main-stability-adaptive-150hz-cpu0p05-rekey2p0-clean-r1` |
| 150 | Adaptive | `20260524-022820-saturation-adaptive-long-main-stability-adaptive-150hz-cpu0p05-rekey2p0-clean-r2` |
| 150 | Adaptive | `20260524-022949-saturation-adaptive-long-main-stability-adaptive-150hz-cpu0p05-rekey2p0-clean-r3` |
| 150 | static-balanced | `20260524-021749-saturation-adaptive-long-main-stability-static-balanced-150hz-cpu0p05-rekey2p0-clean-r1` |
| 150 | static-balanced | `20260524-021916-saturation-adaptive-long-main-stability-static-balanced-150hz-cpu0p05-rekey2p0-clean-r2` |
| 150 | static-balanced | `20260524-022042-saturation-adaptive-long-main-stability-static-balanced-150hz-cpu0p05-rekey2p0-clean-r3` |
| 150 | Heavy | `20260524-021324-saturation-adaptive-long-main-stability-static-heavy-150hz-cpu0p05-rekey2p0-clean-r1` |
| 150 | Heavy | `20260524-021451-saturation-adaptive-long-main-stability-static-heavy-150hz-cpu0p05-rekey2p0-clean-r2` |
| 150 | Heavy | `20260524-021621-saturation-adaptive-long-main-stability-static-heavy-150hz-cpu0p05-rekey2p0-clean-r3` |
| 150 | Lightweight | `20260524-022214-saturation-adaptive-long-main-stability-static-lightweight-150hz-cpu0p05-rekey2p0-clean-r1` |
| 150 | Lightweight | `20260524-022348-saturation-adaptive-long-main-stability-static-lightweight-150hz-cpu0p05-rekey2p0-clean-r2` |
| 150 | Lightweight | `20260524-022520-saturation-adaptive-long-main-stability-static-lightweight-150hz-cpu0p05-rekey2p0-clean-r3` |
| 200 | Adaptive | `20260524-024445-saturation-adaptive-long-main-stability-adaptive-200hz-cpu0p05-rekey2p0-clean-r1` |
| 200 | Adaptive | `20260524-024614-saturation-adaptive-long-main-stability-adaptive-200hz-cpu0p05-rekey2p0-clean-r2` |
| 200 | Adaptive | `20260524-024746-saturation-adaptive-long-main-stability-adaptive-200hz-cpu0p05-rekey2p0-clean-r3` |
| 200 | Adaptive | `20260524-033915-saturation-adaptive-long-cpu-sensitivity-adaptive-200hz-cpu0p05-rekey2p0-clean-r1` |
| 200 | Adaptive | `20260524-034043-saturation-adaptive-long-cpu-sensitivity-adaptive-200hz-cpu0p05-rekey2p0-clean-r2` |
| 200 | Adaptive | `20260524-034212-saturation-adaptive-long-cpu-sensitivity-adaptive-200hz-cpu0p05-rekey2p0-clean-r3` |
| 200 | Adaptive | `20260524-040912-saturation-adaptive-long-cpu-sensitivity-adaptive-200hz-cpu0p1-rekey2p0-clean-r1` |
| 200 | Adaptive | `20260524-041024-saturation-adaptive-long-cpu-sensitivity-adaptive-200hz-cpu0p1-rekey2p0-clean-r2` |
| 200 | Adaptive | `20260524-041136-saturation-adaptive-long-cpu-sensitivity-adaptive-200hz-cpu0p1-rekey2p0-clean-r3` |
| 200 | Adaptive | `20260524-043540-saturation-adaptive-long-cpu-sensitivity-adaptive-200hz-cpu0p25-rekey2p0-clean-r1` |
| 200 | Adaptive | `20260524-043645-saturation-adaptive-long-cpu-sensitivity-adaptive-200hz-cpu0p25-rekey2p0-clean-r2` |
| 200 | Adaptive | `20260524-043749-saturation-adaptive-long-cpu-sensitivity-adaptive-200hz-cpu0p25-rekey2p0-clean-r3` |
| 200 | static-balanced | `20260524-023547-saturation-adaptive-long-main-stability-static-balanced-200hz-cpu0p05-rekey2p0-clean-r1` |
| 200 | static-balanced | `20260524-023720-saturation-adaptive-long-main-stability-static-balanced-200hz-cpu0p05-rekey2p0-clean-r2` |
| 200 | static-balanced | `20260524-023852-saturation-adaptive-long-main-stability-static-balanced-200hz-cpu0p05-rekey2p0-clean-r3` |
| 200 | static-balanced | `20260524-033016-saturation-adaptive-long-cpu-sensitivity-static-balanced-200hz-cpu0p05-rekey2p0-clean-r1` |
| 200 | static-balanced | `20260524-033146-saturation-adaptive-long-cpu-sensitivity-static-balanced-200hz-cpu0p05-rekey2p0-clean-r2` |
| 200 | static-balanced | `20260524-033315-saturation-adaptive-long-cpu-sensitivity-static-balanced-200hz-cpu0p05-rekey2p0-clean-r3` |
| 200 | static-balanced | `20260524-040156-saturation-adaptive-long-cpu-sensitivity-static-balanced-200hz-cpu0p1-rekey2p0-clean-r1` |
| 200 | static-balanced | `20260524-040308-saturation-adaptive-long-cpu-sensitivity-static-balanced-200hz-cpu0p1-rekey2p0-clean-r2` |
| 200 | static-balanced | `20260524-040422-saturation-adaptive-long-cpu-sensitivity-static-balanced-200hz-cpu0p1-rekey2p0-clean-r3` |
| 200 | static-balanced | `20260524-042910-saturation-adaptive-long-cpu-sensitivity-static-balanced-200hz-cpu0p25-rekey2p0-clean-r1` |
| 200 | static-balanced | `20260524-043016-saturation-adaptive-long-cpu-sensitivity-static-balanced-200hz-cpu0p25-rekey2p0-clean-r2` |
| 200 | static-balanced | `20260524-043120-saturation-adaptive-long-cpu-sensitivity-static-balanced-200hz-cpu0p25-rekey2p0-clean-r3` |
| 200 | Heavy | `20260524-023118-saturation-adaptive-long-main-stability-static-heavy-200hz-cpu0p05-rekey2p0-clean-r1` |
| 200 | Heavy | `20260524-023247-saturation-adaptive-long-main-stability-static-heavy-200hz-cpu0p05-rekey2p0-clean-r2` |
| 200 | Heavy | `20260524-023417-saturation-adaptive-long-main-stability-static-heavy-200hz-cpu0p05-rekey2p0-clean-r3` |
| 200 | Heavy | `20260524-032543-saturation-adaptive-long-cpu-sensitivity-static-heavy-200hz-cpu0p05-rekey2p0-clean-r1` |
| 200 | Heavy | `20260524-032715-saturation-adaptive-long-cpu-sensitivity-static-heavy-200hz-cpu0p05-rekey2p0-clean-r2` |
| 200 | Heavy | `20260524-032845-saturation-adaptive-long-cpu-sensitivity-static-heavy-200hz-cpu0p05-rekey2p0-clean-r3` |
| 200 | Heavy | `20260524-035813-saturation-adaptive-long-cpu-sensitivity-static-heavy-200hz-cpu0p1-rekey2p0-clean-r1` |
| 200 | Heavy | `20260524-035929-saturation-adaptive-long-cpu-sensitivity-static-heavy-200hz-cpu0p1-rekey2p0-clean-r2` |
| 200 | Heavy | `20260524-040044-saturation-adaptive-long-cpu-sensitivity-static-heavy-200hz-cpu0p1-rekey2p0-clean-r3` |
| 200 | Heavy | `20260524-042555-saturation-adaptive-long-cpu-sensitivity-static-heavy-200hz-cpu0p25-rekey2p0-clean-r1` |
| 200 | Heavy | `20260524-042700-saturation-adaptive-long-cpu-sensitivity-static-heavy-200hz-cpu0p25-rekey2p0-clean-r2` |
| 200 | Heavy | `20260524-042806-saturation-adaptive-long-cpu-sensitivity-static-heavy-200hz-cpu0p25-rekey2p0-clean-r3` |
| 200 | Lightweight | `20260524-024021-saturation-adaptive-long-main-stability-static-lightweight-200hz-cpu0p05-rekey2p0-clean-r1` |
| 200 | Lightweight | `20260524-024149-saturation-adaptive-long-main-stability-static-lightweight-200hz-cpu0p05-rekey2p0-clean-r2` |
| 200 | Lightweight | `20260524-024321-saturation-adaptive-long-main-stability-static-lightweight-200hz-cpu0p05-rekey2p0-clean-r3` |
| 200 | Lightweight | `20260524-033446-saturation-adaptive-long-cpu-sensitivity-static-lightweight-200hz-cpu0p05-rekey2p0-clean-r1` |
| 200 | Lightweight | `20260524-033618-saturation-adaptive-long-cpu-sensitivity-static-lightweight-200hz-cpu0p05-rekey2p0-clean-r2` |
| 200 | Lightweight | `20260524-033745-saturation-adaptive-long-cpu-sensitivity-static-lightweight-200hz-cpu0p05-rekey2p0-clean-r3` |
| 200 | Lightweight | `20260524-040533-saturation-adaptive-long-cpu-sensitivity-static-lightweight-200hz-cpu0p1-rekey2p0-clean-r1` |
| 200 | Lightweight | `20260524-040647-saturation-adaptive-long-cpu-sensitivity-static-lightweight-200hz-cpu0p1-rekey2p0-clean-r2` |
| 200 | Lightweight | `20260524-040759-saturation-adaptive-long-cpu-sensitivity-static-lightweight-200hz-cpu0p1-rekey2p0-clean-r3` |
| 200 | Lightweight | `20260524-043225-saturation-adaptive-long-cpu-sensitivity-static-lightweight-200hz-cpu0p25-rekey2p0-clean-r1` |
| 200 | Lightweight | `20260524-043333-saturation-adaptive-long-cpu-sensitivity-static-lightweight-200hz-cpu0p25-rekey2p0-clean-r2` |
| 200 | Lightweight | `20260524-043436-saturation-adaptive-long-cpu-sensitivity-static-lightweight-200hz-cpu0p25-rekey2p0-clean-r3` |
| 300 | Adaptive | `20260524-030255-saturation-adaptive-long-main-stability-adaptive-300hz-cpu0p05-rekey2p0-clean-r1` |
| 300 | Adaptive | `20260524-030427-saturation-adaptive-long-main-stability-adaptive-300hz-cpu0p05-rekey2p0-clean-r2` |
| 300 | Adaptive | `20260524-030557-saturation-adaptive-long-main-stability-adaptive-300hz-cpu0p05-rekey2p0-clean-r3` |
| 300 | static-balanced | `20260524-025345-saturation-adaptive-long-main-stability-static-balanced-300hz-cpu0p05-rekey2p0-clean-r1` |
| 300 | static-balanced | `20260524-025517-saturation-adaptive-long-main-stability-static-balanced-300hz-cpu0p05-rekey2p0-clean-r2` |
| 300 | static-balanced | `20260524-025646-saturation-adaptive-long-main-stability-static-balanced-300hz-cpu0p05-rekey2p0-clean-r3` |
| 300 | Heavy | `20260524-024915-saturation-adaptive-long-main-stability-static-heavy-300hz-cpu0p05-rekey2p0-clean-r1` |
| 300 | Heavy | `20260524-025045-saturation-adaptive-long-main-stability-static-heavy-300hz-cpu0p05-rekey2p0-clean-r2` |
| 300 | Heavy | `20260524-025215-saturation-adaptive-long-main-stability-static-heavy-300hz-cpu0p05-rekey2p0-clean-r3` |
| 300 | Lightweight | `20260524-025817-saturation-adaptive-long-main-stability-static-lightweight-300hz-cpu0p05-rekey2p0-clean-r1` |
| 300 | Lightweight | `20260524-025949-saturation-adaptive-long-main-stability-static-lightweight-300hz-cpu0p05-rekey2p0-clean-r2` |
| 300 | Lightweight | `20260524-030122-saturation-adaptive-long-main-stability-static-lightweight-300hz-cpu0p05-rekey2p0-clean-r3` |

## Artifacts

- Comparison CSV: `thesis-report-mac-full/comparison/comparison.csv`
- Comparison JSON: `thesis-report-mac-full/comparison/comparison.json`
- Comparison plot: `thesis-report-mac-full/comparison/comparison_metrics.svg`
- Sweep plot: `thesis-report-mac-full/comparison/sweep_metrics.svg`
- cpu_sensitivity.svg: `thesis-report-mac-full/comparison/cpu_sensitivity.svg`
- rekey_sensitivity.svg: `thesis-report-mac-full/comparison/rekey_sensitivity.svg`
- network_impairment.svg: `thesis-report-mac-full/comparison/network_impairment.svg`

Each comparison row now carries `source_run_dir`, and the table above identifies the exact run directory used for each point.
Per-run folders under the results root contain the individual latency histograms and adaptive switch plots.
- Results root: `thesis-report-mac-full`
