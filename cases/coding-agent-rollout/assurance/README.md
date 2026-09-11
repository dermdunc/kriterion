# Assurance evidence fixture (AUTHORED)

Both files in this directory are **hand-authored fixtures**, exactly like every other
evidence item in this case pack (ADR-003: `attestation: AUTHORED`). No assurance system
ran; no capability named here exists; every digest is a placeholder.

They exist to demonstrate the generic assurance-evidence document contract Kriterion can
consume (ADR-007, `src/kriterion/assurance/adapter.py`):

- `envelope.json` — an `AssuranceEvidenceEnvelope` (0.x document shape): one result per
  eval spec, explicit critical-failure and coverage-gap (`fingerprint.uncovered`) lists.
- `decision.json` — the producer's five-state decision over that envelope
  (`REVIEW_REQUIRED` here: prompt-injection resilience is partial, runtime drift is
  unmeasurable).

Import them with:

```bash
kriterion assurance import cases/coding-agent-rollout/assurance --attestation AUTHORED
```

The reference producer of this document shape is Hekton Assurance's 0.x envelope
(a separate, domain-independent project); Kriterion reads the documents only and never
imports its code. The shape carries **no committee, investment or Kriterion concept** —
that is the point of the boundary in both directions.
