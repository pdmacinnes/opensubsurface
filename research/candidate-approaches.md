# Candidate research approaches

Status: provisional research directions. None has been implemented or demonstrated by OpenSubsurface.

This comparison expands the [initial research assessment](initial-research-report.md). Novelty remains uncertain. The literature already contains adaptive surveys, Bayesian design, passive imaging, joint inversion, and underground acquisition.

## A. Resolve competing three-dimensional explanations with adaptive ERT

**Hypothesis:** measurements selected to discriminate rival geometries, with nuisance uncertainty included, can reduce acquisition cost more effectively than optimizing average image resolution.

Examples include one connected resistive inclusion versus two separated inclusions, or a shallow broad anomaly versus a deeper compact anomaly.

The ambition is a substantial efficiency gain while retaining calibrated uncertainty and identifying impossible cases.

**Established foundations:** optimized and adaptive ERT are existing methods. Bayesian design has also been applied across geophysics, including combined DC/IP surveys. [Wilkinson et al., 2015](https://academic.oup.com/gji/article/203/1/755/586360), [DC/IP study, 2024](https://doi.org/10.1016/j.jconhyd.2024.104452), [Strutz and Curtis, 2024](https://academic.oup.com/gji/article/236/3/1309/7492801)

**Novelty opportunity:** a specific method that resolves geometry ambiguities under realistic low-cost acquisition errors, tested against strong existing designs. Neither adaptivity nor Bayesian reasoning alone is novel.

The [focused follow-up review](prior-art-review.md) identifies closer target-specific Bayesian ERT and nuisance-aware EIT design. Originality remains unconfirmed. The [observability pilot](../specs/ert-observability-pilot.md) is a proposed feasibility study rather than a new design method.

**First software test:** compare sequential discrimination designs with standard arrays, static optimized designs, and adaptive resolution-based designs. Use independent solvers and ambiguous controls.

**Falsification:** gains disappear against strong baselines, different forward models, or broader geology.

**Potential impact:** fewer acquisition commands or less survey time for a defined inference task. This is not equivalent to universal increases in map depth or resolution.

**Expense:** no sensor purchase for simulation. Later validation could use borrowed ERT equipment or an open hardware instrument. Obtain a real configuration budget only after instrument requirements are known.

## B. Optimize the value of limited underground access

**Hypothesis:** a few observations from an existing underground opening can provide more useful information than many extra surface observations.

Possible access includes an existing tunnel, basement, or research borehole. Robot mapping could supply geometry and guide geophysical sensor placement.

This changes observation geometry and may address weakly observed directions that image processing cannot recover.

**Established foundations:** borehole tomography and tunnel-ahead imaging exist. A numerical elastic inversion study compared acquisition configurations around a tunnel. [Riedel et al., 2022](https://arxiv.org/abs/2202.03208)

**Novelty opportunity:** selecting sparse accessible locations under placement uncertainty and a strict cost budget. The claim would concern information gained per feasible access point.

**First software test:** compare added underground positions with added surface sensors. Vary location errors and accessible-region constraints.

**Falsification:** gains require unrealistic accuracy, extensive access, or targets almost touching the sensors.

**Potential impact:** better recoverability through new observation directions. This may be more consequential than improvements to surface-only reconstruction.

**Expense:** software exploration first. Physical cost depends on existing access, sensor placement, and positioning. The direction does not initially require purchasing a robot or drilling a borehole.

## C. Extract information from opportunistic seismic sources

**Hypothesis:** explicit modeling of traffic or machinery sources, including their uncertainty, can recover information discarded by conventional averaging.

An ambitious target is stable recovery of cavity-related scattered or late-arriving energy from a sparse sensor array.

**Established foundations:** infrastructure noise has supported near-surface imaging through dark-fiber distributed acoustic sensing. Passive seismic tunnel-anomaly detection has also been checked by drilling. [Ajo-Franklin et al., 2019](https://www.nature.com/articles/s41598-018-36675-8), [Wang et al., 2022](https://doi.org/10.1016/j.jappgeo.2022.104718)

**Novelty opportunity:** robustness to moving unknown sources and sparse heterogeneous sensors. Passive sensing or using traffic alone is not novel.

**First software test:** generate elastic wavefields with moving sources, unknown wavelets, attenuation, timing errors, and cavity-free confounders. Compare with correlation and surface-wave analysis.

**Falsification:** inferred structures change substantially with source direction, or useful frequencies fall below realistic sensor sensitivity.

**Potential impact:** repeated observations without a controlled source. Fine cavity geometry remains a more demanding hypothesis than broad velocity structure.

**Expense:** no sensors for simulation. Later expense may be dominated by synchronization, coupling, and array size. A DAS interrogator is not recommended as an initial purchase.

## D. Fuse observations while tolerating structural disagreement

**Hypothesis:** locally variable relationships between measurement methods can reduce false geological interpretations while preserving useful fusion gains.

Possible combinations are ERT with seismic measurements or ERT with GPR.

A successful method would identify supported common boundaries while allowing electrical-only or mechanical-only changes.

**Established foundations:** cross-gradient coupling, petrophysical inversion, and probabilistic integration already exist. Cross-gradient artifacts have been examined explicitly. [Gallardo and Meju, 2004](https://doi.org/10.1029/2003JB002716), [Astic, Heagy, and Oldenburg](https://www.appliedgeophysics.org/articles/2021-astic-etal-gji.pdf), [Recoverability study, 2022](https://academic.oup.com/gji/article/230/3/1489/6561617)

**Novelty opportunity:** a precise failure benchmark and measured improvement in uncertainty or interpretation. Adding a coupling penalty does not establish an original contribution.

**First software test:** generate shared geological boundaries plus conductivity-only and elasticity-only changes. Compare separate inversion, established joint inversion, and a disagreement-tolerant alternative.

**Falsification:** better calibration comes only from very broad intervals or effectively ignoring one measurement method.

**Potential impact:** fewer unsupported interpretations, particularly when soil moisture and geological boundaries differ.

**Expense:** simulations first. Physical work eventually needs paired data or two acquisition systems. Existing published data would reduce expense only if suitable geometry, metadata, ground truth, and licensing are available.

## Comparison

These are qualitative judgments from the reviewed evidence, not numerical scores or demonstrated outcomes.

| Direction | Scientific plausibility | Novelty opportunity | Potential impact | Simulation feasibility | Later cost driver |
| --- | --- | --- | --- | --- | --- |
| A. Adaptive ambiguity-focused ERT | High for observable tasks; gain magnitude unknown | Unconfirmed; close prior art | High if survey time falls substantially | High | ERT acquisition and validation geometry |
| B. Limited underground access | High for geometry benefit; economical deployment unknown | Moderate | Potentially very high | High for ERT, moderate for elastic imaging | Access and positioning |
| C. Opportunistic seismic sources | High for broad structure; fine cavity geometry uncertain | Moderate | High if sparse sensors suffice | Moderate | Synchronization, coupling, array size |
| D. Disagreement-tolerant fusion | High for reducing incorrect coupling | Moderate within an active field | High for reliable interpretation | Moderate | Paired measurements and validation |

All initial software studies have zero required hardware spending and no paid AI API requirement. Compute, storage, electricity, and researcher time still have costs.

Start with A. Investigate B if the surface data are insufficient. Evaluate D after trustworthy single-method baselines exist. Keep C as a higher-risk alternative.

The [recommended direction](recommended-direction.md) and [draft protocol](first-experiment.md) define the proposed initial scope.
