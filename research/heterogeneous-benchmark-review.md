# Choosing an independent heterogeneous DC benchmark

Review date: October 8, 2026, America/Denver. Status: literature and protocol review only. No benchmark implementation or new forward simulation was performed for this review.

Subsequent execution: the user approved the spec on October 9, 2026. The [twelve-state contact study](../experiments/ert-contact-benchmark/results/2026-10-09/RESULTS.md) completed and remains inconclusive. The review below records the reasoning before execution.

**Recommendation:** start with an exact vertical-contact reference, evaluated with the existing three-dimensional pyGIMLi solver. Treat it as a necessary interface and boundary diagnostic. It cannot certify the original sphere responses.

The [completed numerical follow-up](../experiments/ert-numerical-validation/results/2026-10-08/RESULTS.md) found that accurate homogeneous voltages do not establish accurate heterogeneous responses. Its fitted sphere comparisons still fail convergence checks. The next reference must therefore be independent of those meshes and sensitive to conductivity contrasts.

## Candidate comparison

The judgments below are project assessments, not measured implementation costs or new scientific findings.

| Reference | Independent basis | Fit to our problem | Remaining reference uncertainty | Decision |
| --- | --- | --- | --- | --- |
| Two quarter-spaces separated by a vertical plane | Closed-form image solution | Same surface point sources; exact interface placement; arbitrary three-dimensional source/receiver coordinates | Formula transcription, sign, and unit mistakes can be checked with boundary identities and literal values | First diagnostic |
| Two horizontal layers | Image series or independently checked Hankel transform | Tests depth-dependent heterogeneity and outer boundaries; planar interfaces avoid curved-volume aliasing | Series truncation or digital-filter error must have a numerical bound | Useful second planar diagnostic |
| Finite-contrast sphere below an insulating surface | Published harmonic/image treatments and sphere benchmarks | Closest to the original one-body geometry | Must establish the exact formula, sphere/image coupling, truncation error, and accessible reference code/data | Required later for inclusion certification |
| Geoana sphere in a uniform field in an infinite medium | Existing analytical implementation | Tests some material-interface behavior but changes both excitation and domain | Its mathematical solution does not represent the surface-electrode experiment | Do not substitute for the original sphere reference |

The contact and layered models have restricted material geometry. Running a three-dimensional solver on them tests three-dimensional point-source fields; it does not demonstrate resolution of arbitrary three-dimensional bodies.

## What the original sources establish

Van Nostrand and Cook's [USGS Professional Paper 499](https://pubs.usgs.gov/publication/pp499) derives the vertical-fault image solution on printed pages 52-53, equations 21-23. The reflection and transmission coefficients follow from continuity of potential and normal current. We inspected the original PDF and rendered those equation pages to resolve OCR ambiguities. The [reference note](contact-reference.md) restates the formula in conductivity notation and gives independent checks.

[Li and Spitzer (2002)](https://doi.org/10.1046/j.1365-246X.2002.01819.x), section 2 and the later examples, explain why the choice of primary field and finite-domain boundaries matters in heterogeneous DC modelling. Their discussion supports testing boundary truncation separately from local refinement. It does not identify the cause of our current errors.

[Tang, Wang, and Ren (2010)](https://html.rhhz.net/dqwlxb/2010-03-26.htm), section 4.1, use a vertical-contact model to compare an adaptive finite-element calculation with an analytical solution. Their material model is invariant along strike and their numerical method is 2.5D. Their convergence result is evidence that the contact is an established benchmark, not a performance prediction for our solver.

[Boulanger and Chouteau (2005)](https://doi.org/10.1111/j.1365-2478.2005.00484.x) compare charge-density integral-equation calculations against analytical and finite-difference results for layered and vertical-contact models. We reviewed the publisher abstract, not a runnable release of their solver.

The existing [SimPEG layered-earth source](https://github.com/simpeg/simpeg/blob/main/simpeg/electromagnetics/static/resistivity/simulation_1d.py) uses digital linear filtering. The installed 0.25.2 source exposes that capability. A result from it would be a useful independent formulation, but numerical transform accuracy still needs checking. Calling a method semi-analytical does not make its output an exact reference automatically.

### Sphere references need an additional audit

[Ren and Tang (2014)](https://doi.org/10.1093/gji/ggu245), section 3.2, report a sphere benchmark with radius 2.25 m, center depth 4.5 m, resistivity 10,000 ohm m in a 100 ohm m background, and a surface point source. They cite Van Nostrand and Cook for the analytical response. The paper also demonstrates goal-oriented mesh refinement, which is established prior art rather than a new OpenSubsurface technique.

[Ren and Tang (2010)](https://doi.org/10.1190/1.3298690) report three-dimensional adaptive modelling against analytical models. The indexed paper identifies a peer-reviewed software location at `software.seg.org/2010/0002`; this review could not retrieve a working release from that location. We did not execute its code or obtain raw reference arrays. This does not establish that all copies are unavailable.

The USGS report contains several distinct sphere treatments, including uniform-field solutions, perfectly conducting limits, and more general harmonic/image discussion. These have different assumptions. We inspected the discussion of sphere/image interaction on printed page 25 and the perfectly conducting derivation on pages 248-249. Those pages alone do not supply a verified finite-contrast implementation for our original geometries. We must trace the exact finite-contrast formulation and bound its series error before treating a sphere curve as ground truth.

[Geoana's documentation](https://geoana.simpeg.xyz/api/generated/geoana.em.static.ElectrostaticSphere.html) and installed `ElectrostaticSphere.potential` source describe a uniform electrostatic field in a whole space. Replacing our electrode field with a uniform field, or adding a mirrored sphere without accounting for interaction, would create a different reference problem. Neither shortcut is authorized by the proposed contact study.

## Proposed hypothesis and falsification

Hypothesis: pyGIMLi's existing DC formulation can reproduce an exact, mesh-aligned vertical-contact response at the original voltage-error thresholds within a two-hour worker budget and 8 GiB process cap.

The [proposed spec](../specs/ert-contact-benchmark.md) fixes two heterogeneous contrast states, one homogeneous control, four mesh configurations, and the original survey. Failure to meet the reference and padding gates within that scope falsifies the proposed computational feasibility claim for this configuration set. It does not prove that the PDE formulation is incapable of accuracy or that the subsurface is physically unobservable.

The analytical reference is independent of pyGIMLi's mesh and field calculation. No exact contact field will be supplied as the native solver's primary field or outer-boundary values. That separation matters because supplying the complete known solution could make this heterogeneous check trivial.

A pass would establish conditional accuracy for the declared contact voltages. The next step would still be a separately reviewed finite-contrast sphere reference and convergence study. No geometry bank, adaptive acquisition, or hardware result follows automatically.

## Review provenance and unresolved access

The public USGS PDF was retrieved from [the original report URL](https://pubs.usgs.gov/pp/0499/report.pdf). Its SHA-256 was `03932c9d5fbf8d7afaa965a5558c4035d08cac52dfabc5dcc820833bc8600578`. The downloaded PDF, extracted text, and page images remain in ignored local output; the repository publishes citations and original notes.

We reviewed the complete relevant contact pages, selected sphere pages, the accessible original 2014 article sections, and the cited publisher records. The 2010 sphere paper was available through indexed excerpts and an institutional bibliographic record; we did not inspect a complete downloadable copy during this review. The SEG code URL was inaccessible. Reference availability and numerical error bounds remain explicit requirements for the later sphere stage.

Established findings are the documented analytical solutions and published benchmark use. The solver feasibility claim is a project hypothesis. Transfer from a passing contact benchmark to accurate sphere or two-body responses remains speculation.
