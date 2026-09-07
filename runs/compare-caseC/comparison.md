# Kriterion Comparison

## Condition A (5 run(s))

- Unsupported-claim rate: 0.000
- Category-inflation count: 0
- Numeric-alteration count: 0
- Belief-update rationality: 1.0
- Dissent non-empty rate: 1.0
- P0 pass rate: 1.000

## Condition B (5 run(s))

- Unsupported-claim rate: 0.000
- Category-inflation count: 0
- Numeric-alteration count: 0
- Belief-update rationality: None
- Dissent non-empty rate: None
- P0 pass rate: 1.000

## Condition C (5 run(s))

- Unsupported-claim rate: 0.000
- Category-inflation count: 0
- Numeric-alteration count: 0
- Belief-update rationality: 0.9166666666666666
- Dissent non-empty rate: 1.0
- P0 pass rate: 1.000

## Pre-registered honest-negative criterion (docs/experiment-plan.md)

**Fired:** True

C beats both A and B on 0/2-of-3-available sub-metrics ([]), by bare aggregate comparison -- NOT the pre-registered 2x-seed-stddev margin (not implemented; seed_to_seed_stddev() is unused here) or the >2x-inference-cost condition (cost is not tracked at all, a separately documented gap). A true margin-and-cost check could only make it HARDER for C to beat a sub-metric, never easier, so this is a stricter-than-shown result if fully evaluated, not a weaker one. perturbation-robustness sub-metric not computed (needs the P1 batch).

