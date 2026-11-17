# Ensemble study: bird-dev-vllm-64 + bird-dev-t05

1534 questions (1334 held-out, 200 for choosing the weight). Selection: weighted vote over the least-flagged candidates (CAV-3). Δ, lost/won and p are on the held-out questions against `bird-dev-vllm-64 only, K=64`.

Oracle (any correct sample): bird-dev-vllm-64 82.8%, bird-dev-t05 78.0%, union 83.8%

| Config | All | Tune | Held-out | Δ held-out [CI95] | Lost / won | p |
|---|---|---|---|---|---|---|
| bird-dev-vllm-64 only, K=64 | 66.95 | 71.5 | 66.27 | +0.00 [+0.00, +0.00] | 0 / 0 | 1.000 |
| bird-dev-t05 only, K=32 | 64.86 | 70.0 | 64.09 | -2.17 [-3.30, -0.97] | 45 / 16 | 0.000 |
| bird-dev-vllm-64 only, K=32 | 66.69 | 72.0 | 65.89 | -0.37 [-1.20, +0.37] | 18 / 13 | 0.473 |
| bird-dev-vllm-64 only, K=48 | 66.62 | 71.5 | 65.89 | -0.37 [-0.97, +0.15] | 10 / 5 | 0.302 |
| same budget: base 48 + extra 16, w=0.5 | 66.95 | 72.0 | 66.19 | -0.07 [-0.67, +0.52] | 9 / 8 | 1.000 |
| same budget: base 48 + extra 16, w=0.75 | 66.82 | 72.0 | 66.04 | -0.22 [-0.82, +0.45] | 11 / 8 | 0.648 |
| same budget: base 48 + extra 16, w=1.0 | 66.95 | 72.0 | 66.19 | -0.07 [-0.75, +0.60] | 10 / 9 | 1.000 |
| same budget: base 48 + extra 16, w=1.5 | 66.82 | 72.0 | 66.04 | -0.22 [-0.90, +0.45] | 13 / 10 | 0.678 |
| same budget: base 48 + extra 16, w=2.0 | 66.62 | 72.0 | 65.82 | -0.45 [-1.20, +0.37] | 17 / 11 | 0.345 |
| more samples: base 64 + extra 16, w=0.5 | 67.01 | 72.0 | 66.27 | +0.00 [-0.37, +0.37] | 4 / 4 | 1.000 |
| more samples: base 64 + extra 16, w=0.75 | 66.95 | 72.0 | 66.19 | -0.07 [-0.52, +0.37] | 5 / 4 | 1.000 |
| more samples: base 64 + extra 16, w=1.0 | 67.01 | 72.5 | 66.19 | -0.07 [-0.52, +0.37] | 6 / 5 | 1.000 |
| more samples: base 64 + extra 16, w=1.5 | 67.08 | 72.5 | 66.27 | +0.00 [-0.60, +0.60] | 8 / 8 | 1.000 |
| more samples: base 64 + extra 16, w=2.0 | 67.01 | 72.5 | 66.19 | -0.07 [-0.67, +0.52] | 9 / 8 | 1.000 |
| same budget: base 32 + extra 32, w=0.5 | 66.43 | 72.0 | 65.59 | -0.67 [-1.50, +0.07] | 18 / 9 | 0.122 |
| same budget: base 32 + extra 32, w=0.75 | 66.17 | 72.0 | 65.29 | -0.97 [-1.80, -0.22] | 22 / 9 | 0.029 |
| same budget: base 32 + extra 32, w=1.0 | 66.49 | 72.0 | 65.67 | -0.60 [-1.42, +0.22] | 20 / 12 | 0.215 |
| same budget: base 32 + extra 32, w=1.5 | 66.10 | 71.0 | 65.37 | -0.90 [-1.80, -0.07] | 24 / 12 | 0.065 |
| same budget: base 32 + extra 32, w=2.0 | 66.17 | 71.5 | 65.37 | -0.90 [-1.80, +0.00] | 24 / 12 | 0.065 |
| more samples: base 64 + extra 32, w=0.5 | 66.88 | 72.0 | 66.12 | -0.15 [-0.67, +0.37] | 7 / 5 | 0.774 |
| more samples: base 64 + extra 32, w=0.75 | 66.82 | 72.0 | 66.04 | -0.22 [-0.82, +0.37] | 9 / 6 | 0.607 |
| more samples: base 64 + extra 32, w=1.0 | 66.88 | 72.0 | 66.12 | -0.15 [-0.75, +0.45] | 10 / 8 | 0.815 |
| more samples: base 64 + extra 32, w=1.5 | 66.82 | 72.0 | 66.04 | -0.22 [-0.97, +0.45] | 12 / 9 | 0.664 |
| more samples: base 64 + extra 32, w=2.0 | 66.75 | 72.0 | 65.97 | -0.30 [-0.97, +0.45] | 14 / 10 | 0.541 |
