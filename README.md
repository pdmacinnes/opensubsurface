# OpenSubsurface

**Mapping the world beneath us.**

OpenSubsurface is an independent, civilian research project investigating whether three-dimensional subsurface sensing and mapping can become more accessible and affordable.

The long-term vision is to combine inexpensive sensors, physics-based reconstruction, and distributed measurements to understand the ground beneath us. Potential applications include infrastructure inspection, geology, groundwater research, underground robotics, and future underground transportation.

## Why this research matters

Surface maps describe exposed terrain. Underground maps usually come from indirect measurements of electrical, electromagnetic, elastic, or gravitational properties. Those measurements do not uniquely identify every object or material beneath the surface.

Existing geophysical methods already produce useful three-dimensional images. Their limitations include weak sensitivity at depth, attenuation, restricted measurement geometry, uncertain acquisition conditions, and ambiguous interpretation.

OpenSubsurface asks where a small independent team can make a measurable contribution. The goal is to improve useful information per unit of acquisition cost while reporting uncertainty and failure conditions.

## Current status

**Simulation pilot implemented; numerical validation remains inconclusive.**

The initial literature assessment recommends studying adaptive electrical resistivity tomography (ERT). The proposed method would select measurements that distinguish competing three-dimensional anomaly geometries and account for acquisition uncertainty.

Adaptive ERT, Bayesian inversion, and optimized survey design already exist. We have not invented a new sensing technology, demonstrated an efficiency gain, or validated a mapping system.

The [first numerical profiles](experiments/ert-observability-pilot/results/2026-10-08/RESULTS.md) failed the strict continuum-reference accuracy gate. The finest tested configuration also exceeded the projected compute budget. The full geometry and nuisance bank were not run. These results do not establish a physical observability limit.

The proposed experiment is a draft research protocol. Its numerical targets are hypotheses and design choices, not results.

A [focused prior-art review](research/prior-art-review.md) identifies closer target-specific and nuisance-aware design methods. Originality remains unconfirmed. The [approved observability pilot](specs/ert-observability-pilot.md) is implemented with explicit numerical and resource gates. The [approved validation-only follow-up](experiments/ert-numerical-validation/README.md) compares tensor and octree meshes, audits source handling, and checks four existing inclusion geometries. It found substantial mesh-dependent voltage and body-volume errors. Independent inclusion accuracy is still unverified; geometry discrimination and acquisition-efficiency claims remain premature.

The [heterogeneous benchmark review](research/heterogeneous-benchmark-review.md) recommends an exact vertical-contact diagnostic before further sphere work. The [proposed contact spec](specs/ert-contact-benchmark.md) fixes the analytical reference, controlled mesh comparisons, resource budget, and failure criteria. It has not been implemented or run, and a contact pass would leave sphere accuracy unverified.

## Research goals

- Identify physical observability limits separately from engineering and cost constraints.
- Reuse established open-source geophysical solvers and documented experimental findings.
- Test candidate methods against strong baselines and independent forward models.
- Distinguish anomaly detection, localization, shape recovery, and material identification.
- Publish reproducible methods, uncertainty estimates, negative results, and failure cases.
- Establish a compelling simulation result before purchasing hardware.

## Scope

The project covers sensing, inverse problems, survey design, and interpretation. It is civilian research and does not develop tunneling machinery or weapons.

The initial hypothesis concerns selected shallow electrical anomaly geometries. It does not promise arbitrary high-resolution imaging through ground or definitive cavity identification from resistivity alone.

## Project organization

| Directory | Purpose |
| --- | --- |
| [research/](research/) | Literature assessment, references, candidate directions, hypotheses, and proposed experiments |
| [experiments/](experiments/) | Future simulations, raw measurements, and experimental results |
| [docs/](docs/) | Project status, evidence conventions, and reproducibility documentation |

Start with the [initial research report](research/initial-research-report.md), [candidate comparison](research/candidate-approaches.md), and [annotated references](research/references.md).

The [recommended direction](research/recommended-direction.md) and [broader experiment draft](research/first-experiment.md) describe the long-term research hypothesis. The [pilot README](experiments/ert-observability-pilot/README.md) gives reproduction commands, and the [feature map](FEATURE_MAP.md) records actual verification status.

## Scientific standards

An established finding must point to an original paper or technical source and describe the conditions under which it holds. A project hypothesis must state what could falsify it. Speculation must be labeled and cannot be presented as demonstrated capability.

A detailed reconstruction is not proof of an accurate map. Evaluation must address independent measurements, model mismatch, uncertainty calibration, and cases that the observations cannot distinguish.

## Contributing

At this stage, useful contributions include corrections to the literature assessment, closer prior art, geophysical review of the proposed experiment, and stronger baselines.

Use issues and pull requests for substantive changes. Discuss experimental scope before adding software or hardware designs. Do not submit credentials, private datasets, employer materials, or third-party content without redistribution rights.

## License

The original repository content is licensed under the [Apache License 2.0](LICENSE).

References link to external work. External software, datasets, papers, and hardware retain their own licenses. A reference does not grant permission to redistribute that work.
