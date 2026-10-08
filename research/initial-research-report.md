# Initial research assessment

Research reviewed through October 8, 2026. This document records the initial literature assessment. No OpenSubsurface experiment has been implemented or run.

Companion documents contain the [candidate comparison](candidate-approaches.md), [recommended direction](recommended-direction.md), [proposed first experiment](first-experiment.md), and [annotated references](references.md).

## Executive assessment

Making underground mapping more accessible is a credible research objective. A general, high-resolution three-dimensional map of arbitrary ground from inexpensive surface sensors is a much harder proposition.

Surface mapping observes exposed surfaces directly. Subsurface mapping usually measures fields or waves that combine information over volumes, lose energy, and reach sensors through limited geometries. Different underground configurations can produce indistinguishable measurements.

The project must separate three objectives.

| Objective | Meaning of success | Present feasibility |
| --- | --- | --- |
| Map accessible underground space | Reconstruct tunnel or cave walls and robot trajectories | Demonstrated; robustness remains difficult |
| Image physical properties through ground | Estimate conductivity, wave speed, permittivity, or density | Established, with variable resolution and uncertainty |
| Recover underground objects and geology | Identify cavities, pipes, fractures, materials, and connectivity | Possible for selected targets; often ambiguous |

A detailed voxel volume is not sufficient evidence of an accurate map.

The recommended starting point is uncertainty-aware adaptive electrical resistivity tomography (ERT). The proposed method would distinguish selected competing three-dimensional electrical anomaly geometries with fewer measurements than strong existing designs.

A factor-of-two reduction in acquisition cost is a research target, not a predicted or demonstrated result. Adaptive surveying, Bayesian inversion, and sensor fusion already have substantial prior work. Originality requires a validated advance against those methods.

## Evidence categories and review limits

- **Established:** supported by a mathematical result, published experiment, or documented software capability. The finding applies within the conditions of that source.
- **Hypothesis:** plausible and testable, but unverified in the proposed setting.
- **Speculation:** a possible future extension without adequate evidence.
- **Project result:** an outcome produced and verified by OpenSubsurface. There are no project results yet.

This is a focused literature assessment, not an exhaustive systematic review or proof of novelty. Some sources were available as abstracts, author manuscripts, or technical documentation. Their reported findings have not been independently reproduced by this project. The [reference notes](references.md) identify the evidence used and its limits.

## Existing methods

### Electrical resistivity tomography

ERT injects current through electrodes and measures voltage differences at other electrodes. Its primary reconstruction is electrical conductivity or resistivity.

**Established:** three-dimensional and time-lapse ERT are mature capabilities. Multi-electrode instrumentation, survey optimization, and numerical inversion already support complex surveys. [Loke et al., 2013](https://www.sciencedirect.com/science/article/pii/S0926985113000499)

ERT has relatively simple sensing electronics and responds to moisture, salinity, clay, and some cavities or buried structures. Resistivity is not a unique material identifier. A resistive anomaly might reflect dry sediment, competent rock, an air-filled cavity, or another resistive body.

Surface measurements lose sensitivity to small and deep structures. Software may display a model below the region constrained by observations. Oldenburg and Li introduced a depth-of-investigation diagnostic to reveal dependence on the reference model. It is an interpretation aid, not a universal cutoff or a complete uncertainty analysis. [Oldenburg and Li, 1999](https://basin.earth.ncu.edu.tw/Course/SeminarII/abstract2009_1/reference_abstracts/0408-1_abstract_5Estimating%20depth%20of%20in%20dc%20resistivity%20and%20IP%20surveys.pdf)

**Assessment:** ERT is a useful low-cost research platform. Initial claims should concern electrical anomalies and their geometry, rather than definitive cavity or material labels.

### Seismic tomography and full-waveform inversion

Seismic methods infer elastic properties through wave propagation. Approaches use first-arrival times, surface-wave dispersion, reflected or scattered waves, or full waveforms.

First-arrival tomography is comparatively robust but discards much of the recorded information. Full-waveform inversion (FWI) can recover finer detail, with stronger dependence on physical modeling, source characterization, initialization, and optimization.

**Established field result:** a Rice University tunnel experiment used a 24 m survey line, 25 shots, and 72 receivers. Joint travel-time and waveform inversion recovered subwavelength features in a relatively simple shallow setting. The paper discusses limitations of representing an air-filled void as an acoustic low-velocity region. This is evidence for selected target recovery, not unrestricted high-resolution imaging. [Tunnel inversion study, 2020](https://doi.org/10.1016/j.jappgeo.2020.103957)

FWI can converge to incorrect solutions when modeled and observed waveforms are sufficiently misaligned, commonly called cycle skipping. An analytical example shows that wavefield reconstruction inversion can also suffer this failure. This is an optimization problem, distinct from whether the observations contain the necessary information. [Symes, 2020](https://arxiv.org/abs/2003.14181)

**Assessment:** seismic imaging has substantial potential. Convincing near-surface work must eventually address elastic waves, attenuation, surface waves, source uncertainty, and realistic cavities. A clean acoustic simulation is preliminary evidence.

### Ground-penetrating radar

Ground-penetrating radar (GPR) measures electromagnetic reflections and propagation effects. Its observations depend on dielectric properties, conductivity, interfaces, and object geometry.

GPR can resolve fine shallow detail in favorable ground. Conductive clay and saline water can severely attenuate the signal. USGS field studies document clay layers that partly or completely prevent imaging below them. [USGS field investigation](https://pubs.usgs.gov/wri/1997/4042/report.pdf)

**Established:** crosshole GPR waveform inversion recovered a subwavelength waveguiding layer at a Swiss aquifer test site. Borehole access and informative waveguide behavior were important conditions. [Klotzsche et al., 2012](https://www.research.ed.ac.uk/en/publications/crosshole-gpr-full-waveform-inversion-of-waveguides-acting-as-pre/)

A 2026 publication reports GPU-accelerated dual-parameter three-dimensional GPR inversion with numerical experiments and a field example. The reviewed abstract does not establish broad field reliability or an unrestricted software license. Using PyTorch and a GPU for three-dimensional GPR inversion is already prior art. [GPR inversion study, 2026](https://doi.org/10.1016/j.cageo.2025.106101)

**Assessment:** GPR is attractive for software feasibility studies and selected environments. It does not support a promise of universal penetration through ground.

### Sensor fusion

Different methods measure different properties. Combining them may constrain explanations that remain ambiguous under a single method.

**Established:** joint resistivity-seismic inversion using cross-gradient constraints was demonstrated on synthetic and field data in 2004. The constraint encourages shared structural boundaries. [Gallardo and Meju, 2004](https://doi.org/10.1029/2003JB002716)

Petrophysically guided approaches incorporate relationships among physical properties and geological classes. An implementation and reproducible examples are available through SimPEG. [Astic, Heagy, and Oldenburg](https://www.appliedgeophysics.org/articles/2021-astic-etal-gji.pdf)

Physical properties do not always share boundaries. Moisture can alter conductivity without producing the same mechanical boundary. Forcing agreement can introduce convincing artifacts.

**Assessment:** research should test when fusion supplies independently supported information and when it imposes an incorrect relationship.

### Underground robotic mapping

Robots equipped with lidar, cameras, thermal sensors, and inertial sensors can reconstruct accessible underground spaces despite darkness, dust, communication loss, and difficult terrain.

**Established:** CERBERUS demonstrated autonomous underground exploration and mapping in the DARPA Subterranean Challenge. Public datasets contain onboard measurements from four ANYmal robots during the final event. [CERBERUS dataset](https://github.com/leggedrobotics/cerberus_darpa_subt_datasets/blob/main/README.md)

These sensors map observable surroundings. They do not reveal arbitrary structures behind tunnel walls.

**Assessment:** robotics becomes especially relevant when it moves geophysical sensors to useful underground positions or supplies accurate acquisition geometry. The project is independent civilian research; use of a published robotics benchmark does not imply affiliation with its sponsors.

### Gravity and muon imaging

Gravity and gravity gradients respond to density contrasts. They can detect cavities without electromagnetic penetration, but weak signals, environmental corrections, and ambiguous density distributions limit interpretation.

A quantum gravity gradiometer detected a 2 m tunnel in a field experiment. Horizontal localization was tighter than depth estimation. The reported 0.5 m survey spacing is not 0.5 m volumetric reconstruction accuracy. [Stray et al., 2022](https://www.nature.com/articles/s41586-021-04315-3)

Muon radiography measures attenuation of naturally occurring cosmic-ray muons. ScanPyramids detected a void at least 30 m long with three independent detector technologies. This was a strong detection result without a complete geometry reconstruction. [Morishima et al., 2017](https://www.nature.com/articles/nature24647)

Muon measurements require suitable trajectories through the target to the detector. For ordinary ground, placement below or beside the region is often essential.

**Assessment:** neither quantum gravimetry nor muography is the best initial hardware investment for this project.

## Physical and mathematical limitations

A useful observation model is

$$
d = F(m,g,\eta)+\epsilon,
$$

where `m` describes underground physical properties, `g` describes acquisition geometry, `eta` contains nuisance variables, and `epsilon` is measurement noise.

A reconstruction may fail because information is absent, too weak to measure, or not extracted correctly by the algorithm. These need different remedies.

| Limitation | Nature | Possible remedy |
| --- | --- | --- |
| Different configurations produce indistinguishable data | Observability or identifiability | New measurement physics, geometry, or justified prior information |
| Deep or fine structure produces weak changes | Physical sensitivity and stability | Better geometry, lower noise, larger aperture |
| Wave energy is attenuated before returning | Physical propagation | Different frequency or method, shorter path, underground access |
| Observations cover restricted directions | Acquisition geometry | Additional views or existing underground access |
| Electrode errors, clocks, coupling, or source uncertainty corrupt data | Engineering and modeling | Calibration and explicit nuisance estimation |
| Inversion finds a poor local optimum | Algorithmic | Better initialization, objectives, optimization, multiscale methods |
| Images depend strongly on assumed geology | Prior or model dependence | Broader model families and uncertainty analysis |

### Finite measurements do not determine arbitrary detail

Near a candidate model,

$$
\Delta d \approx J\Delta m,
$$

where `J` is the sensitivity matrix.

Weakly sensitive directions are difficult to recover. Directions in its null space cannot be recovered locally from those observations.

Increasing voxel count does not increase information. More measurement combinations help only when they add useful sensitivity.

Linear reciprocal electrical measurements reuse a finite electrode-response operator. Combinatorially many four-electrode configurations do not provide that many independent spatial observations. Repeated measurements may improve noise estimates and precision without adding new spatial directions.

### Uniqueness and stability differ

An ideal inverse problem can have a unique solution while remaining unstable. Small observation errors can correspond to large differences in reconstructed structure.

Mathematical results establish exponential instability for classes of elliptic inverse inclusion and scattering problems. They support caution about fine interior reconstruction from boundary data. They do not supply a universal numerical resolution limit for every ERT survey. [Di Cristo and Rondi](https://arxiv.org/abs/math/0303126)

### Wavelength is a scale rather than an absolute recovery floor

For waves, `lambda = v / f`. Bandwidth, aperture, attenuation, illumination, and signal-to-noise ratio determine useful resolution.

Subwavelength detection or parameter estimation is possible under favorable conditions, as the cited GPR and seismic experiments show. Locating one assumed object is easier than reconstructing arbitrary structure at the same spatial scale.

### Material labels require additional information

Two differently labeled objects with identical conductivity fields produce identical ideal DC electrical responses. This follows from the forward model.

ERT cannot establish their material identity from DC data alone. A classifier trained on restricted examples does not remove that ambiguity.

### Correlated errors do not average away

Independent noise can decrease with repeated observations. Geometry errors, persistent source bias, instrument drift, and model errors may remain.

Electrode position errors can produce substantial ERT artifacts. Recent Bayesian approximation-error work addresses such uncertainty explicitly. This treatment is also existing prior art. [Position sensitivity study, 2005](https://academic.oup.com/gji/article/163/1/1/2087311), [Räsänen et al., 2026](https://onlinelibrary.wiley.com/doi/10.1002/nsg.70079)

**Consequence:** reconstruction can reduce wasted measurements and expose uncertainty. Broad gains in depth and resolution will probably require better acquisition geometry or complementary physical measurements.

## Demonstrations that define the baseline

| Existing result | What it establishes | What it does not establish |
| --- | --- | --- |
| [Optimized ERT, 2012](https://core.ac.uk/download/pdf/2800724.pdf) | Survey design can account for noise, polarization, and multichannel efficiency | A new opportunity merely from selecting electrode combinations |
| [Adaptive ERT, 2015](https://academic.oup.com/gji/article/203/1/755/586360) | A laboratory adaptive survey improved imaging of a moving insulating target | Unrestricted three-dimensional recovery in heterogeneous field ground |
| [Bayesian DC/IP design, 2024](https://doi.org/10.1016/j.jconhyd.2024.104452) | Combined electrical survey optimization at a virtual contamination site | Physical validation of the proposed OpenSubsurface task |
| [Time-aware ERT design, 2025](https://doi.org/10.1029/2025WR040444) | A synthetic study addressed spatial resolution versus acquisition time | A measured acquisition advantage for static geometry discrimination |
| [Passive tunnel imaging, 2022](https://doi.org/10.1016/j.jappgeo.2022.104718) | An anomaly at roughly 60-100 m depth was detected and checked by drilling | Complete tunnel geometry recovered at that depth |

The passive tunnel study used 136 nodal seismometers and two hours of ambient noise. Its result does not establish that a small inexpensive array can do the same.

The adaptive laboratory ERT target was approximately invariant in one direction. Its geometry and tank boundaries matter when interpreting the result.

## Open-source foundations

| Resource | Documented capability | Proposed use |
| --- | --- | --- |
| [SimPEG](https://github.com/simpeg/simpeg) | Geophysical simulation, inversion, and sensitivities; MIT | Primary ERT platform and baselines |
| [pyGIMLi](https://github.com/gimli-org/pygimli) | Geophysical modeling and inversion; Apache 2.0 | Independent numerical checks |
| [gprMax](https://gprmax.org/) | Electromagnetic FDTD with GPU support | GPR feasibility studies |
| [Deepwave](https://github.com/ar4/deepwave) | Differentiable acoustic and elastic propagation on CPUs and GPUs; MIT | Seismic extensions |
| [OhmPi](https://ohmpi.org/) | Open hardware resistivity meter | Possible later physical validation |
| [CERBERUS data](https://github.com/leggedrobotics/cerberus_darpa_subt_datasets) | Underground robot measurements | Acquisition geometry and mapping research |
| [SubT ground truth](https://github.com/subtchallenge/systems_tunnel_ground_truth) | Underground point clouds and course information | Accessible-space evaluation |

License descriptions concern the named projects. Check pinned versions, dependencies, and dataset terms before redistribution. References do not relicense external work.

The gprMax GPU solver was published in 2019. Its historical speedups are evidence that commodity GPUs can help, not a performance forecast for this project. [Warren et al., 2019](https://doi.org/10.1016/j.cpc.2018.11.007)

pyGIMLi provides a three-dimensional tank example with insulating boundaries. A successful tank reconstruction does not automatically establish field performance. [Tank example](https://www.pygimli.org/_examples_auto/3_ert/plot_modTank3d/)

OhmPi's 2026 paper reports a configuration below EUR 1,500 for 16 electrodes and circuit and field validation. This is a published configuration, not a delivered quote or a complete larger-survey budget. No purchase is recommended now. [Clément et al., 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13377445/)

OpenFWI provides synthetic seismic benchmarks rather than field ground truth. Its published supplement describes BSD licensing for code and CC BY-NC-SA for data. The project should generate its own openly licensed synthetic datasets for unrestricted redistribution. [OpenFWI supplement](https://proceedings.neurips.cc/paper_files/paper/2022/file/27d3ef263c7cb8d542c4f9815a49b69b-Supplemental-Datasets_and_Benchmarks.pdf)

## Recommended research sequence

Start with [ambiguity-focused adaptive ERT](recommended-direction.md). It provides a relatively accessible way to isolate information limits and measurement efficiency.

If surface observations are insufficient, investigate the value of limited underground access. Evaluate disagreement-tolerant fusion after a single-method benchmark is trustworthy. Opportunistic seismic imaging remains a higher-risk alternative.

All four [candidate directions](candidate-approaches.md) can begin without sensor purchases or paid AI APIs.

## Compute and reproducibility

An RTX 5070 Ti has 16 GB of standard GPU memory. This can help local wave-propagation experiments, but does not establish that large three-dimensional inversions or posterior ensembles fit. [NVIDIA specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5070-family/)

For the proposed ERT study, CPU sparse solves and system RAM may matter more than GPU throughput. Start with existing solvers and modest parameterized model families. Profile before custom acceleration.

For seismic work, validate small elastic models before large three-dimensional experiments. For GPR, fine sampling and stored wavefields can make modest volumes expensive.

No language model is required in the reconstruction loop. Existing numerical methods and local experiments can test the central hypothesis.

Publish the frozen protocol, deviations, model definitions, measurements, versions, seeds, baseline tuning, failures, and resource use. [Reproducibility requirements](../docs/reproducibility.md) describe the intended record.

## Established findings, hypotheses, and speculation

| Established | Hypotheses | Speculation |
| --- | --- | --- |
| Three-dimensional geophysical property imaging exists | Task-specific acquisition can outperform general image optimization | A widely deployable distributed subsurface observatory |
| Open ERT hardware exists | Explicit nuisance treatment can preserve adaptive efficiency gains | Affordable general high-resolution mapping at substantial depth |
| Geometry affects recoverability | Sparse underground access can add disproportionate information | Robots progressively building richer geophysical maps |
| Joint inversion and passive imaging have field demonstrations | Fusion that tolerates disagreement can reduce false interpretations | Reliable material and connectivity recovery across diverse geology |
| Some explanations are observationally indistinguishable | A benchmark can identify when another measurement method is necessary | Universal reconstruction from inexpensive surface-only sensors |

The next research step is a focused novelty check and expert review of the [draft experiment protocol](first-experiment.md). Implementation and hardware selection require a separate approved scope.
