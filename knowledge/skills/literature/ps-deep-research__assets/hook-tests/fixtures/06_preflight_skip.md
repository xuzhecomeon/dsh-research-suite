---
declared_tier: deep
pre_flight:
  predicted_phases:
    - phase_2: will_run
    - phase_5: will_run
phases:
  phase_2: ran
  phase_5: skipped
---

# Preflight skip fixture

声明了 phase_5 会跑但实际 skipped,preflight 应判 FAIL。
