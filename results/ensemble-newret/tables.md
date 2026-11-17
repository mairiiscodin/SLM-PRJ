# Ensemble study: bird-dev-vllm-64 + bird-dev-newret

1534 questions (1334 held-out, 200 for choosing the weight). Selection: weighted vote over the least-flagged candidates (CAV-3). Δ, lost/won and p are on the held-out questions against `bird-dev-vllm-64 only, K=64`.

Oracle (any correct sample): bird-dev-vllm-64 82.8%, bird-dev-newret 76.3%, union 83.2%

| Config | All | Tune | Held-out | Δ held-out [CI95] | Lost / won | p |
|---|---|---|---|---|---|---|
| bird-dev-vllm-64 only, K=64 | 66.95 | 71.5 | 66.27 | +0.00 [+0.00, +0.00] | 0 / 0 | 1.000 |
| bird-dev-newret only, K=16 | 65.38 | 70.0 | 64.69 | -1.57 [-2.85, -0.37] | 44 / 23 | 0.014 |
| bird-dev-vllm-64 only, K=48 | 66.62 | 71.5 | 65.89 | -0.37 [-0.97, +0.15] | 10 / 5 | 0.302 |
| same budget: base 48 + extra 16, w=0.5 | 67.14 | 72.0 | 66.42 | +0.15 [-0.52, +0.82] | 9 / 11 | 0.824 |
| same budget: base 48 + extra 16, w=0.75 | 67.14 | 72.5 | 66.34 | +0.07 [-0.60, +0.75] | 10 / 11 | 1.000 |
| same budget: base 48 + extra 16, w=1.0 | 67.14 | 72.5 | 66.34 | +0.07 [-0.67, +0.82] | 11 / 12 | 1.000 |
| same budget: base 48 + extra 16, w=1.5 | 66.95 | 72.0 | 66.19 | -0.07 [-0.82, +0.67] | 14 / 13 | 1.000 |
| same budget: base 48 + extra 16, w=2.0 | 66.82 | 72.0 | 66.04 | -0.22 [-0.97, +0.60] | 16 / 13 | 0.711 |
| more samples: base 64 + extra 16, w=0.5 | 67.28 | 71.5 | 66.64 | +0.37 [-0.07, +0.82] | 2 / 7 | 0.180 |
| more samples: base 64 + extra 16, w=0.75 | 67.28 | 72.0 | 66.57 | +0.30 [-0.15, +0.75] | 3 / 7 | 0.344 |
| more samples: base 64 + extra 16, w=1.0 | 67.14 | 72.5 | 66.34 | +0.07 [-0.52, +0.60] | 7 / 8 | 1.000 |
| more samples: base 64 + extra 16, w=1.5 | 67.14 | 72.5 | 66.34 | +0.07 [-0.52, +0.67] | 8 / 9 | 1.000 |
| more samples: base 64 + extra 16, w=2.0 | 67.01 | 72.0 | 66.27 | +0.00 [-0.60, +0.60] | 10 / 10 | 1.000 |
