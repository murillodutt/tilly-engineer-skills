---
tds_id: mesh.maturity_layer_gate_evidence
tds_class: mesh
status: active
consumer: adapter authors and benchmark authors
source_of_truth: false
evidence_level: L1
tver: 0.3.169
---

# Maturity Layer Gate Evidence

This note records the compact evidence basis for the TES Maturity Layer Gate.
It is not a broad theory document; `docs/mesh/PRINCIPLES.md` owns the contract.

## Observed Regression

In a private canary project (source-of-record kept off the TES repository), an
agent treated `Simplicity First` as a flat rule and attempted to simplify mature
adapter/installer surfaces by removing compatibility structure that existed to
protect installed behavior. The inverse risk appeared during review: once
`Evolution` and `Platform` were named, a vague promotion could allow speculative
architecture unless the evidence fields were checked.

The gate therefore protects both directions:

- `Birth` without promotion evidence must reject future scaffolding;
- `Evolution` and `Platform` must preserve accepted contracts, compatibility,
  fallback, and release oracles even when local code would become shorter.

## Evidence Map

| Source | TES use |
|--------|---------|
| Martin Fowler, [YAGNI](https://martinfowler.com/bliki/Yagni.html) | `Birth` remains conservative: do not build presumptive future capabilities or unused extensibility points. |
| Martin Fowler, [Is Design Dead?](https://martinfowler.com/articles/designDead.html) | Evolutionary design is not design absence; mature work needs refactoring and design discipline. |
| Martin Fowler, [Refactoring](https://www.martinfowler.com/books/refactoring.html) | `Evolution` changes should preserve behavior through small transformations and verification. |
| Thoughtworks, [Building Evolutionary Architectures](https://www.thoughtworks.com/en-us/insights/books/building-evolutionary-architectures) | Mature architecture evolves by guided, incremental change while protecting important characteristics. |
| DORA, [Loosely Coupled Teams](https://dora.dev/capabilities/loosely-coupled-teams/) | `Platform` and mature architecture are judged by ability to test, deploy, and change safely, not by local code minimalism. |
| CNCF, [Project Metrics](https://www.cncf.io/project-metrics/) | Promotion should be evidence-based, using adoption, health, and sustainability signals rather than labels alone. |
| CNCF, [Argo Graduation](https://www.cncf.io/announcements/2022/12/06/the-cloud-native-computing-foundation-announces-argo-has-graduated/) | A concrete mature project example: multiple subprojects and production adoption can justify governance and compatibility structure. |

## Operational Translation

The gate blocks two regressions:

- premature complexity in `Birth`;
- simplification regression in `Evolution` or `Platform`.

The promotion rule is deliberately asymmetric: no evidence keeps the task in
`Birth`; evidence must name the protected baseline, allowed complexity,
forbidden complexity, and oracle before higher-layer complexity is accepted.
