# Ensemble study: bird-dev-vllm-64 + bird-dev-prune32

1534 questions (1334 held-out, 200 for choosing the weight). Selection: weighted vote over the least-flagged candidates (CAV-3). Δ, lost/won and p are on the held-out questions against `bird-dev-vllm-64 only, K=64`.

Oracle (any correct sample): bird-dev-vllm-64 82.8%, bird-dev-prune32 79.5%, union 84.2%

| Config | All | Tune | Held-out | Δ held-out [CI95] | Lost / won | p |
|---|---|---|---|---|---|---|
| bird-dev-vllm-64 only, K=64 | 66.95 | 71.5 | 66.27 | +0.00 [+0.00, +0.00] | 0 / 0 | 1.000 |
| bird-dev-prune32 only, K=32 | 67.80 | 71.0 | 67.32 | +1.05 [-0.37, +2.47] | 39 / 53 | 0.175 |
| bird-dev-vllm-64 only, K=32 | 66.69 | 72.0 | 65.89 | -0.37 [-1.20, +0.37] | 18 / 13 | 0.473 |
| bird-dev-vllm-64 only, K=48 | 66.62 | 71.5 | 65.89 | -0.37 [-0.97, +0.15] | 10 / 5 | 0.302 |
| same budget: base 48 + extra 16, w=0.5 | 67.01 | 71.0 | 66.42 | +0.15 [-0.45, +0.75] | 7 / 9 | 0.804 |
| same budget: base 48 + extra 16, w=0.75 | 67.14 | 71.5 | 66.49 | +0.22 [-0.45, +0.90] | 8 / 11 | 0.648 |
| same budget: base 48 + extra 16, w=1.0 | 67.08 | 71.5 | 66.42 | +0.15 [-0.52, +0.82] | 10 / 12 | 0.832 |
| same budget: base 48 + extra 16, w=1.5 | 67.54 | 71.5 | 66.94 | +0.67 [-0.15, +1.57] | 13 / 22 | 0.175 |
| same budget: base 48 + extra 16, w=2.0 | 67.73 | 71.5 | 67.17 | +0.90 [-0.07, +1.87] | 15 / 27 | 0.088 |
| more samples: base 64 + extra 16, w=0.5 | 67.21 | 72.0 | 66.49 | +0.22 [-0.22, +0.75] | 4 / 7 | 0.549 |
| more samples: base 64 + extra 16, w=0.75 | 67.01 | 72.0 | 66.27 | +0.00 [-0.52, +0.52] | 7 / 7 | 1.000 |
| more samples: base 64 + extra 16, w=1.0 | 67.01 | 72.0 | 66.27 | +0.00 [-0.60, +0.60] | 8 / 8 | 1.000 |
| more samples: base 64 + extra 16, w=1.5 | 67.01 | 71.5 | 66.34 | +0.07 [-0.67, +0.82] | 13 / 14 | 1.000 |
| more samples: base 64 + extra 16, w=2.0 | 67.14 | 71.5 | 66.49 | +0.22 [-0.60, +1.05] | 14 / 17 | 0.720 |
| same budget: base 32 + extra 32, w=0.5 | 67.54 | 72.0 | 66.87 | +0.60 [-0.30, +1.50] | 13 / 21 | 0.229 |
| same budget: base 32 + extra 32, w=0.75 | 67.67 | 71.5 | 67.09 | +0.82 [-0.15, +1.80] | 16 / 27 | 0.126 |
| same budget: base 32 + extra 32, w=1.0 | 67.86 | 71.5 | 67.32 | +1.05 [+0.00, +2.02] | 16 / 30 | 0.054 |
| same budget: base 32 + extra 32, w=1.5 | 68.12 | 71.5 | 67.62 | +1.35 [+0.22, +2.47] | 20 / 38 | 0.025 |
| same budget: base 32 + extra 32, w=2.0 | 68.19 | 71.5 | 67.69 | +1.42 [+0.30, +2.62] | 22 / 41 | 0.023 |
| more samples: base 64 + extra 32, w=0.5 | 67.28 | 72.5 | 66.49 | +0.22 [-0.45, +0.90] | 9 / 12 | 0.664 |
| more samples: base 64 + extra 32, w=0.75 | 67.28 | 72.5 | 66.49 | +0.22 [-0.52, +1.05] | 12 / 15 | 0.701 |
| more samples: base 64 + extra 32, w=1.0 | 67.21 | 72.0 | 66.49 | +0.22 [-0.60, +1.05] | 14 / 17 | 0.720 |
| more samples: base 64 + extra 32, w=1.5 | 67.54 | 71.5 | 66.94 | +0.67 [-0.30, +1.57] | 17 / 26 | 0.222 |
| more samples: base 64 + extra 32, w=2.0 | 67.86 | 71.5 | 67.32 | +1.05 [+0.00, +2.10] | 19 / 33 | 0.070 |
