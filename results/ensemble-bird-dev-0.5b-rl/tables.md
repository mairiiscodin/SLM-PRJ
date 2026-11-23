# Ensemble study: bird-dev-0.5b-rl + bird-dev-0.5b-rl-prune32

1534 questions (1334 held-out, 200 for choosing the weight). Selection: weighted vote over the least-flagged candidates (CAV-3). Δ, lost/won and p are on the held-out questions against `bird-dev-0.5b-rl only, K=64`.

Oracle (any correct sample): bird-dev-0.5b-rl 74.5%, bird-dev-0.5b-rl-prune32 73.5%, union 77.6%

| Config | All | Tune | Held-out | Δ held-out [CI95] | Lost / won | p |
|---|---|---|---|---|---|---|
| bird-dev-0.5b-rl only, K=64 | 58.28 | 63.5 | 57.50 | +0.00 [+0.00, +0.00] | 0 / 0 | 1.000 |
| bird-dev-0.5b-rl-prune32 only, K=32 | 59.00 | 61.5 | 58.62 | +1.12 [-0.30, +2.55] | 39 / 54 | 0.146 |
| bird-dev-0.5b-rl only, K=32 | 57.50 | 64.0 | 56.52 | -0.97 [-1.87, +0.00] | 27 / 14 | 0.060 |
| same budget: base 32 + extra 32, w=0.5 | 59.52 | 65.5 | 58.62 | +1.12 [+0.15, +2.10] | 15 / 30 | 0.036 |
| same budget: base 32 + extra 32, w=0.75 | 59.71 | 65.0 | 58.92 | +1.42 [+0.45, +2.47] | 15 / 34 | 0.009 |
| same budget: base 32 + extra 32, w=1.0 | 59.91 | 65.0 | 59.15 | +1.65 [+0.60, +2.77] | 15 / 37 | 0.003 |
| same budget: base 32 + extra 32, w=1.5 | 59.91 | 65.0 | 59.15 | +1.65 [+0.45, +2.77] | 21 / 43 | 0.008 |
| same budget: base 32 + extra 32, w=2.0 | 59.78 | 64.5 | 59.07 | +1.57 [+0.45, +2.77] | 24 / 45 | 0.015 |
| more samples: base 64 + extra 32, w=0.5 | 59.39 | 64.5 | 58.62 | +1.12 [+0.30, +2.02] | 9 / 24 | 0.014 |
| more samples: base 64 + extra 32, w=0.75 | 59.65 | 64.5 | 58.92 | +1.42 [+0.52, +2.32] | 10 / 29 | 0.003 |
| more samples: base 64 + extra 32, w=1.0 | 59.65 | 64.5 | 58.92 | +1.42 [+0.52, +2.40] | 11 / 30 | 0.004 |
| more samples: base 64 + extra 32, w=1.5 | 59.78 | 65.0 | 59.00 | +1.50 [+0.52, +2.47] | 13 / 33 | 0.005 |
| more samples: base 64 + extra 32, w=2.0 | 59.91 | 64.5 | 59.22 | +1.72 [+0.67, +2.77] | 14 / 37 | 0.002 |
