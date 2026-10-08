# References and evidence notes

Research reviewed through October 8, 2026.

These references support the [initial assessment](initial-research-report.md), [candidate comparison](candidate-approaches.md), [recommended direction](recommended-direction.md), and [draft experiment](first-experiment.md).

The notes describe reported evidence and technical documentation. They do not record independent replication by OpenSubsurface. A focused search cannot establish that no closer prior art exists.

Publisher abstracts, accessible author manuscripts, and official project documentation were used where available. No third-party paper, figure, dataset, or software is redistributed here.

## Electrical imaging and survey design

### R01. Recent developments in the direct-current geoelectrical imaging method

Loke et al. (2013). Journal of Applied Geophysics.

[Publisher record](https://www.sciencedirect.com/science/article/pii/S0926985113000499)

Used for the maturity of multi-electrode, three-dimensional, and time-lapse electrical imaging. This review does not establish OpenSubsurface performance.

### R02. Estimating depth of investigation in DC resistivity and IP surveys

Oldenburg, D. W., and Li, Y. (1999). Geophysics, 64(2), 403-416. DOI: 10.1190/1.1444545.

[DOI](https://doi.org/10.1190/1.1444545) | [Accessible paper](https://basin.earth.ncu.edu.tw/Course/SeminarII/abstract2009_1/reference_abstracts/0408-1_abstract_5Estimating%20depth%20of%20in%20dc%20resistivity%20and%20IP%20surveys.pdf)

Used for reference-model dependence and depth-of-investigation interpretation. The diagnostic is not a complete posterior uncertainty analysis.

### R03. Practical aspects of applied optimized survey design for electrical resistivity tomography

Wilkinson, P. B., Loke, M. H., Meldrum, P. I., Chambers, J. E., Kuras, O., Gunn, D. A., and Ogilvy, R. D. (2012). Geophysical Journal International, 189, 428-440. DOI: 10.1111/j.1365-246X.2012.05372.x.

[DOI](https://doi.org/10.1111/j.1365-246X.2012.05372.x) | [Accepted manuscript](https://core.ac.uk/download/pdf/2800724.pdf)

Used for practical design constraints involving noise, polarization, and multichannel acquisition. Defines prior art that an adaptive method must exceed.

### R04. Adaptive time-lapse optimized survey design for electrical resistivity tomography monitoring

Wilkinson et al. (2015). Geophysical Journal International, 203(1), 755-766. DOI: 10.1093/gji/ggv329.

[Original paper](https://academic.oup.com/gji/article/203/1/755/586360)

Reports controlled laboratory validation with a moving insulating cylinder. The approximately invariant target direction and tank geometry limit generalization to arbitrary three-dimensional field imaging.

### R05. Optimized survey design for the joint use of direct current resistivity and induced polarization: Monitoring of DNAPL source zone evolution at a virtual field site

(2024). Journal of Contaminant Hydrology, 267, 104452. DOI: 10.1016/j.jconhyd.2024.104452.

[Publisher record and abstract](https://doi.org/10.1016/j.jconhyd.2024.104452)

Used as prior art for Bayesian combined DC/IP survey design. The cited evaluation is at a virtual field site, not a physical OpenSubsurface test.

### R06. Adaptive multi-objective optimization for real-time monitoring of rapid tracer transport using electrical resistivity tomography: Balancing spatial and temporal resolution

Han et al. (2025). Water Resources Research. DOI: 10.1029/2025WR040444.

[Original paper](https://doi.org/10.1029/2025WR040444)

Reports a synthetic three-dimensional study of spatial resolution and acquisition-time trade-offs. It constrains claims that time-aware adaptive ERT is new.

### R07. Sensitivity of electrical resistivity tomography data to electrode position errors

(2005). Geophysical Journal International, 163(1), beginning at page 1.

[Original paper](https://academic.oup.com/gji/article/163/1/1/2087311)

Used for position sensitivity and inversion artifacts. Error effects depend on acquisition geometry and the underground model.

### R08. Recovery from electrode position uncertainties in geophysical electrical resistance tomography: Application to moisture transport imaging

Räsänen et al. (2026, online publication). Near Surface Geophysics. DOI: 10.1002/nsg.70079.

[Original paper](https://onlinelibrary.wiley.com/doi/10.1002/nsg.70079)

Used as recent prior art for Bayesian approximation-error treatment of uncertain electrode geometry. This does not establish the proposed acquisition-policy gain.

### R09. The simulation of finite ERT electrodes using the complete electrode model

Rücker, C., and Günther, T. (2011). Geophysics, 76(4). DOI: 10.1190/1.3581356.

[DOI](https://doi.org/10.1190/1.3581356)

Used for finite electrode geometry and contact effects. Four-point arrangements reduce some contact effects; their magnitude is not universal. This paper does not justify treating contact resistance as an arbitrary voltage offset.

## Inverse problems and experimental design

### R10. Examples of exponential instability for elliptic inverse problems

Di Cristo, M., and Rondi, L. (2003 preprint).

[Author preprint](https://arxiv.org/abs/math/0303126)

Provides mathematical instability results for classes of elliptic inverse problems. Used to distinguish uniqueness from stable recoverability. It does not give a universal field-survey resolution number.

### R11. Variational Bayesian experimental design for geophysical applications: Seismic source location, amplitude versus offset inversion, and estimating CO2 saturations in a subsurface reservoir

Strutz, D., and Curtis, A. (2024 journal issue; first published online in 2023). Geophysical Journal International, 236(3), 1309-1331. DOI: 10.1093/gji/ggad492.

[Original paper](https://academic.oup.com/gji/article/236/3/1309/7492801) | [Author preprint](https://arxiv.org/abs/2307.01039)

Establishes geophysical prior art for variational Bayesian experiment design. The reviewed applications do not establish performance on the proposed ERT geometry task.

## Seismic and electromagnetic imaging

### R12. Detecting an underground tunnel by applying joint traveltime and waveform inversion

(2020). Journal of Applied Geophysics, article 103957. DOI: 10.1016/j.jappgeo.2020.103957.

[Publisher record, abstract, and section excerpts](https://doi.org/10.1016/j.jappgeo.2020.103957)

Reports synthetic tests and Rice University field measurements. The 24 m line used 25 shots and 72 receivers. Used for selected subwavelength recovery and acoustic-model limitations, not a universal resolution claim.

### R13. Wavefield reconstruction inversion: An example

Symes, W. W. (2020 preprint).

[Author preprint](https://arxiv.org/abs/2003.14181)

An analytical example exposes nonconvexity and possible cycle skipping. Used to separate optimization failures from observation limits.

### R14. Geophysical field investigation at Fort Bragg

U.S. Geological Survey (1997). Water-Resources Investigations Report 97-4042.

[Original USGS report](https://pubs.usgs.gov/wri/1997/4042/report.pdf)

Used for field evidence of partial and complete radar attenuation associated with clay layers. Site-specific penetration limits cannot be transferred directly to another soil.

### R15. Crosshole GPR full-waveform inversion of waveguides acting as preferential flow paths within aquifer systems

Klotzsche, A., van der Kruk, J., Meles, G., and Vereecken, H. (2012). Geophysics, 77(4), H57-H62. DOI: 10.1190/GEO2011-0458.1.

[DOI](https://doi.org/10.1190/GEO2011-0458.1) | [Institutional record and abstract](https://www.research.ed.ac.uk/en/publications/crosshole-gpr-full-waveform-inversion-of-waveguides-acting-as-pre/)

Reports recovery of a subwavelength waveguiding layer in field data. Borehole access and waveguide behavior are important conditions.

### R16. Fast ground penetrating radar dual-parameter full waveform inversion method accelerated by hybrid compilation of CUDA kernel function and PyTorch

(2026 journal issue). Computers & Geosciences, 209, 106101. DOI: 10.1016/j.cageo.2025.106101.

[Publisher record and abstract](https://doi.org/10.1016/j.cageo.2025.106101)

Reports numerical two-dimensional and three-dimensional tests and a field example. Used as prior art for GPU-based GPR inversion. Source licensing and broad field reliability were not established by the reviewed abstract.

### R17. Distributed acoustic sensing using dark fiber for near-surface characterization and broadband seismic event detection

Ajo-Franklin, J. B., et al. (2019). Scientific Reports, 9, 1328. DOI: 10.1038/s41598-018-36675-8.

[Original paper](https://www.nature.com/articles/s41598-018-36675-8)

Reports seven months of measurements along 27 km of dark fiber and near-surface imaging using infrastructure noise. Dense fiber acquisition does not establish equivalence to a small inexpensive sensor array.

### R18. Seismic imaging of mine tunnels by ambient noise along linear arrays

Wang, K., Qian, J., Zhang, H., Gao, J., Bi, D., and Gu, N. (2022). Journal of Applied Geophysics, 203, 104718. DOI: 10.1016/j.jappgeo.2022.104718.

[Publisher record and abstract](https://doi.org/10.1016/j.jappgeo.2022.104718)

Reports 136 nodal seismometers, two hours of noise, an anomaly at approximately 60-100 m depth, and drilling verification. Detection of an anomaly is not complete geometry recovery.

### R19. Elastic waveform inversion in the frequency domain for an application in mechanized tunneling

Riedel, C., Musayev, K., Baitsch, M., and Hackl, K. (2022 preprint).

[Author preprint](https://arxiv.org/abs/2202.03208)

Reports numerical blind tests and a three-dimensional tunnel model with multiple acquisition configurations. Used for geometry-dependent inversion prior art, not field validation.

## Joint interpretation, gravity, and muons

### R20. Joint two-dimensional DC resistivity and seismic travel time inversion with cross-gradients constraints

Gallardo, L., and Meju, M. A. (2004). Journal of Geophysical Research: Solid Earth, 109, B03311. DOI: 10.1029/2003JB002716.

[Original paper](https://doi.org/10.1029/2003JB002716)

Reports synthetic and field joint inversion with structural coupling. Shared-boundary assumptions must be checked when applying this method elsewhere.

### R21. Joint geophysical, petrophysical and geologic inversion using a dynamic Gaussian mixture model

Astic, T., Heagy, L. J., and Oldenburg, D. W. Geophysical Journal International, 224, 40-68 (2021 issue; online publication in 2020).

[Author manuscript](https://www.appliedgeophysics.org/articles/2021-astic-etal-gji.pdf) | [Reproduction repository](https://github.com/simpeg-research/Astic-2020-JointInversion)

Used for petrophysical coupling and existing reproducible SimPEG work. This does not establish that assumed physical-property relationships hold at a new site.

### R22. Towards a better understanding of the recoverability of physical property relationships from geophysical inversions of multiple potential-field data sets

(2022). Geophysical Journal International, 230(3), 1489 onward.

[Original paper](https://academic.oup.com/gji/article/230/3/1489/6561617)

Discusses artifacts associated with cross-gradient coupling. Its potential-field setting is related evidence, not a direct evaluation of the proposed ERT-seismic experiment.

### R23. Quantum sensing for gravity cartography

Stray et al. (2022). Nature. DOI: 10.1038/s41586-021-04315-3.

[Original paper](https://www.nature.com/articles/s41586-021-04315-3)

Reports field detection of a 2 m tunnel with a quantum gravity gradiometer. Distinguish survey spacing, horizontal localization, and depth uncertainty.

### R24. Discovery of a big void in Khufu's Pyramid by observation of cosmic-ray muons

Morishima et al. (2017). Nature, 552, 386-390. DOI: 10.1038/nature24647.

[Original paper](https://www.nature.com/articles/nature24647) | [Accessible paper](https://indico.cern.ch/event/686191/contributions/2814706/attachments/1598584/2533426/nature24647.pdf)

Reports a void at least 30 m long observed with three detector technologies. Detection confidence and a full geometric reconstruction are different claims.

## Software, hardware, and datasets

### R25. SimPEG

Cockett et al. (2015). SimPEG: An open source framework for simulation and gradient based parameter estimation in geophysical applications. Computers & Geosciences, 85, 142-154. DOI: 10.1016/j.cageo.2015.09.015.

[Paper](https://doi.org/10.1016/j.cageo.2015.09.015) | [Repository](https://github.com/simpeg/simpeg) | [License](https://github.com/simpeg/simpeg/blob/main/LICENSE)

Used for existing geophysical simulation and inversion infrastructure. Repository license: MIT.

### R26. pyGIMLi

Rücker, C., Günther, T., and Wagner, F. M. (2017). pyGIMLi: An open-source library for modelling and inversion in geophysics. Computers & Geosciences, 109, 106-123. DOI: 10.1016/j.cageo.2017.07.011.

[Repository](https://github.com/gimli-org/pygimli) | [License](https://www.pygimli.org/about/license/) | [Three-dimensional tank example](https://www.pygimli.org/_examples_auto/3_ert/plot_modTank3d/)

Used for an independent numerical foundation and explicit tank boundary treatment. Project license: Apache 2.0. Dependencies retain their own terms.

### R27. gprMax

Warren, C., Giannopoulos, A., and Giannakis, I. (2016). gprMax: Open source software to simulate electromagnetic wave propagation for ground penetrating radar. Computer Physics Communications, 209, 163-170. DOI: 10.1016/j.cpc.2016.08.020.

[Paper record](https://repository.uwl.ac.uk/id/eprint/5367/) | [Official project](https://gprmax.org/)

The GPU implementation is described in A CUDA-based GPU engine for gprMax: Open source FDTD electromagnetic simulation software (2019), DOI: 10.1016/j.cpc.2018.11.007.

[GPU paper](https://doi.org/10.1016/j.cpc.2018.11.007)

Used for existing electromagnetic simulation and GPU capabilities. The GPU paper specifies GPLv3. Verify the selected release and dependencies before redistribution.

### R28. Deepwave

Richardson, A. Wave propagation modules for PyTorch.

[Repository and documentation](https://github.com/ar4/deepwave) | [License](https://github.com/ar4/deepwave/blob/master/LICENSE)

Current documentation describes acoustic and elastic propagation with CPU and GPU support. Repository license: MIT. No local installation, GPU compatibility check, or benchmark has been run.

### R29. OhmPi

Clément et al. (2026). Design and advances in OhmPi: An open hardware resistivity meter. HardwareX, 27, e00811. DOI: 10.1016/j.ohx.2026.e00811.

[Original paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13377445/) | [Official documentation](https://ohmpi.org/) | [Repository](https://gitlab.com/ohmpi/ohmpi)

Used for open hardware feasibility and published validation. The paper reports a sub-EUR-1,500 16-electrode configuration. This is not a current procurement quote.

Hardware is described under CERN-OHL-S-2.0 and software under GPL-3.0. The article itself has separate publication terms.

### R30. CERBERUS and SubT ground truth

[Dataset repository](https://github.com/leggedrobotics/cerberus_darpa_subt_datasets) | [Final-event README](https://github.com/leggedrobotics/cerberus_darpa_subt_datasets/blob/main/README.md) | [SubT tunnel ground truth](https://github.com/subtchallenge/systems_tunnel_ground_truth)

The dataset repository cites the team's 2022 Science Robotics paper, DOI: 10.1126/scirobotics.abp9742.

[Paper](https://doi.org/10.1126/scirobotics.abp9742)

Used for demonstrated accessible underground mapping and available evaluation resources. Check individual dataset licenses and ground-truth derivation before reuse.

### R31. OpenFWI

Deng et al. (2022). OpenFWI: Large-scale multi-structural benchmark datasets for seismic full waveform inversion. NeurIPS Datasets and Benchmarks.

[Author preprint](https://arxiv.org/abs/2111.02926) | [Code](https://github.com/lanl/OpenFWI) | [Published supplement](https://proceedings.neurips.cc/paper_files/paper/2022/file/27d3ef263c7cb8d542c4f9815a49b69b-Supplemental-Datasets_and_Benchmarks.pdf)

Used for synthetic benchmarking precedent. The supplement specifies BSD code licensing and CC BY-NC-SA 4.0 data licensing. OpenSubsurface should generate independently licensed synthetic data for unrestricted releases.

### R32. NVIDIA RTX 5070 family specifications

[Manufacturer specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5070-family/)

Used only for the RTX 5070 Ti standard 16 GB memory specification. This does not establish solver compatibility, runtime, or a feasible three-dimensional problem size.

### R33. Apache License 2.0

[Official license text](https://www.apache.org/licenses/LICENSE-2.0.txt)

The repository LICENSE contains the official text. This license applies to original project content and does not relicense cited external work.

### R34. Optimized arrays for electrical resistivity tomography survey using Bayesian experimental design

Qiang, S., Shi, X., Kang, X., and Revil, A. (2022). Geophysics, 87(4), E189-E203. DOI: 10.1190/geo2021-0408.1.

[Original paper](https://doi.org/10.1190/geo2021-0408.1) | [Author-uploaded manuscript](https://www.researchgate.net/publication/359357143_Optimized_arrays_for_electrical_resistivity_tomography_survey_using_Bayesian_experimental_design)

Reviewed in the focused follow-up through the author-uploaded manuscript. Reports target-specific Bayesian survey design, superposition-based response reuse, and synthetic comparisons. These are existing precedents rather than OpenSubsurface inventions. Publisher access was unavailable during the follow-up.

### R35. Laplace-based strategies for Bayesian optimal experimental design with nuisance uncertainty

Bartuska, A., Espath, L., and Tempone, R. (2025 issue; published online December 13, 2024). Statistics and Computing, 35, 12. DOI: 10.1007/s11222-024-10544-z.

[Original open-access paper](https://doi.org/10.1007/s11222-024-10544-z)

Reviewed original article sections on marginalized nuisance uncertainty and numerical EIT examples. Relevant mathematical precedent, not a direct surface-geophysical validation.

### R36. A method of fast, sequential experimental design for linearized geophysical inverse problems

Coles, D. A., and Morgan, F. D. (2009). Geophysical Journal International, 178(1), 145-158. DOI: 10.1111/j.1365-246X.2009.04156.x.

[Original paper](https://academic.oup.com/gji/article/178/1/145/2065780)

Reviewed original article material on efficient determinant-based design and the limited number of independent electrical observations. Sequential design and response redundancy are established prior art.

### R37. Comparing well and geophysical data for temperature monitoring within a Bayesian experimental design framework

Thibaut et al. (2022). Water Resources Research, 58(11), e2022WR033045. DOI: 10.1029/2022WR033045.

[Original paper](https://doi.org/10.1029/2022WR033045)

Reviewed original article sections on Bayesian evidential learning, observation combinations, and protocol selection. Used to trace closer ERT design work and identify prediction-focused precedents.

### R38. Optimal Bayesian experimental design for electrical impedance tomography in medical imaging

Karimi, A., Taghizadeh, L., and Heitzinger, C. (2021). Computer Methods in Applied Mechanics and Engineering, 373, 113489. DOI: 10.1016/j.cma.2020.113489.

[Original publisher record and abstract](https://doi.org/10.1016/j.cma.2020.113489)

Reviewed abstract and article excerpts on expected-information-gain design. The medical EIT geometry differs from surface ERT.

### R39. Bayesian experimental design for head imaging by electrical impedance tomography

Hyvönen, N., Jääskeläinen, A., Maity, R., and Vavilov, A. (2023 preprint).

[Author preprint](https://arxiv.org/abs/2312.10383)

Reviewed author abstract describing offline and adaptive A-optimal electrode-placement methods. This is related prior art rather than a field geophysics result.

## Before asserting novelty

Follow citations and citing papers for task-specific acquisition, nonlinear model discrimination, nuisance-aware survey design, and adaptive uncertainty estimation.

Record the search scope and closest comparisons. Absence of a matching result in this initial review is not evidence that a method is new.
