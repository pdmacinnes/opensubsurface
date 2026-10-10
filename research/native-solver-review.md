# Native solver path review

Review date: October 9, 2026, America/Denver. Scope: installed-source inspection, construction-only mesh probes, and one diagnostic correction. No additional contact voltage solve or new mesh-accuracy result is included.

Subsequent execution: the [approved P2 comparison](../experiments/ert-p2-contact-comparison/results/2026-10-09/RESULTS.md) completed six state solves. The fourfold target is not supported, and contact accuracy remains inconclusive. The review below preserves the reasoning before those runs.

**Recommendation:** test explicit P2 elements on the original coarse A and C material cells, under a separate bounded spec. Our direct path uses the supplied mesh without the framework's automatic H2 refinement. This is a verified path distinction, not proof that element order causes the full accuracy failure.

The [contact study](../experiments/ert-contact-benchmark/results/2026-10-09/RESULTS.md) remains inconclusive. Its raw voltages and checksums have not been replaced.

## Verified execution path

The executed adapter creates `ERTModelling(sr=True)`, assigns data, calls `setMesh(..., ignoreRegionManager=True)`, maps one resistivity per cell, calls the native `calculate`, and converts DataMap transfer resistances to signed volts using 0.001 A. This matches the installed `ert.simulate` direct-calculation branch.

The installed `MeshModelling.setMesh` branch for `ignoreRegionManager=True` sets the supplied mesh and returns. It bypasses the region-managed `createFwdMesh_` path. The managed path calls `createRefinedFwdMesh`, whose installed defaults are H2 enabled and P2 disabled. [The upstream framework source](https://github.com/gimli-org/pyGIMLi/blob/362b69893f5abcacb0b36cbfff2934605ecfe3f2/pygimli/frameworks/modelling.py) provides a reference; hashes of the actually inspected installed files are in the evidence record.

The [ERT documentation](https://www.pygimli.org/_modules/pygimli/physics/ert/ert/) mentions P2 in geometric-factor calculation. With `calcOnly=True`, that geometric-factor branch is skipped. The documentation does not establish that a flat-earth signed-voltage calculation automatically uses P2 elements. P2 used to calculate a topographic primary field is another distinct operation.

Switching `ignoreRegionManager` off is not a controlled element-order change. The managed route can also introduce region/background interpretation and model mapping. An explicit P2 mesh followed by explicit material assignment is the cleaner diagnostic for our per-cell benchmark.

## Construction-only evidence

We exercised four tiny hexahedral cells in the installed library without a voltage calculation:

| Path | Cells | Nodes | Nodes per cell |
| --- | ---: | ---: | ---: |
| Input mesh | 4 | 18 | 8 |
| Direct assignment with region manager ignored | 4 | 18 | 8 |
| Managed forward-mesh creation | 32 | 75 | Not needed for this probe |
| Explicit `createP2()` | 4 | 51 | 20 |

The P2 construction retains the tested cell centers and markers. It does **not** retain the tested cell attributes. The next experiment must assign resistivities after construction and verify them; inheriting attributes would be an incorrect shortcut.

These probes contain no survey calculation. Geometry construction does not demonstrate accuracy, solver compatibility, or memory feasibility for a full P2 state solve.

The [evidence record](native-solver-review-evidence.json) contains source hashes, binary hashes, version fields, and probe outputs. To reproduce the central structural distinction in the pinned environment:

```python
import pygimli as pg
from pygimli.physics import ert

mesh = pg.createGrid(x=[-1, 0, 1], y=[-1, 0, 1], z=[-1, 0])
mesh.setCellMarkers([1, 2, 1, 2])
mesh.setCellAttributes([100, 1000, 100, 1000])
direct = ert.ERTModelling(sr=True)
direct.setMesh(mesh, ignoreRegionManager=True)
managed = ert.ERTModelling(sr=True)
managed.setMesh(mesh)
quadratic = mesh.createP2()
for name, value in (("input", mesh), ("direct", direct.mesh()),
                    ("managed", managed.mesh()), ("P2", quadratic)):
    print(name, value.cellCount(), value.nodeCount())
print("P2 attributes", list(quadratic.cellAttributes()))
```

This is a geometry inspection only. Its no-electrode setup can emit calibration/setup messages; it never calls `calculate` or `response`.

## Secondary-field assembly

The compiled core reports `libgimli-v1.6.0-4-g9076db0e`. We resolved that revision to [9076db0efdadad36b38554858b832ff6b1a800cd](https://github.com/gimli-org/pyGIMLi/tree/9076db0efdadad36b38554858b832ff6b1a800cd), and reviewed its native source rather than relying only on current `main`. A reported revision and binary hashes improve provenance; compiler settings and unrecorded build patches remain outside this review.

In [DCSR `preCalculate` and `calculateK`](https://github.com/gimli-org/pyGIMLi/blob/9076db0efdadad36b38554858b832ff6b1a800cd/core/src/bert/dcfemmodelling.cpp), the secondary calculation builds a material-dependent operator `S` and a corresponding unit-resistivity operator `S1` on the working mesh, including boundary terms. The analytical primary field is scaled using source-local resistivity. The discrete right-hand side has the form

`b = S1 * u_primary / rho_source - S * u_primary`.

The native solver calculates the secondary solution and adds the primary field. This explains why a homogeneous result is weak evidence: for constant resistivity, the material and unit-resistivity operators scale together and the secondary right-hand side cancels, subject to the native constraints. Agreement with the homogeneous primary does not test the accuracy of heterogeneous secondary-field approximation.

The explicit analytical-output flag is initialized false in the reviewed native source; the project does not enable it. The observed homogeneous agreement therefore does not require assuming that the project selected that separate shortcut.

A contact aligned with faces removes material-volume aliasing, but it does not remove interpolation, integration, or finite-boundary approximation from the secondary calculation. The source review identifies where these factors enter. It does not measure their individual errors or establish a defect in native assembly.

## Diagnostic correction

The [native header](https://github.com/gimli-org/pyGIMLi/blob/9076db0efdadad36b38554858b832ff6b1a800cd/core/src/bert/dcfemmodelling.h) initializes an optional primary-mesh pointer to null, while the mesh getter returns a reference through that pointer. The flat analytical-primary path does not need a numerical primary mesh. The previous contact adapter queried this optional getter and recorded the unusable return as unavailable.

The adapter now avoids that query and records its reason. A focused test fails if the diagnostic invokes the optional getter. The field calculation, material assignment, current, voltage extraction, and acceptance metrics are unchanged. No new native accuracy run is claimed for this metadata correction.

## Version-provenance correction

The recorded `pygimli_runtime_version` strings must not be interpreted as compiled-build identifiers. In this installation, the Python version helper searches for Git metadata from the installed package path inside the workspace. It resolves the enclosing OpenSubsurface repository. The probe's reported Python revision equals the project's `662988107a6617317d8ad5889c0a4e4b66850e86` commit, while the native core independently reports the `9076db0e` build.

The correct distinction is distribution version, Python-reported version, native-core build string, and binary/source hashes. The evidence record includes them separately. The original environment JSON remains a historical record of the values actually reported; this review corrects their interpretation rather than rewriting that history.

The contact preparation code now captures `pg.core.versionStr()`, hashes of the extension and bundled native libraries, and installed Python source hashes. It labels the Python-reported version's role explicitly. A Python version string that happens to match the project's current commit is not native-code provenance.

## Ranked hypotheses and unresolved questions

| Hypothesis | Evidence | Current conclusion |
| --- | --- | --- |
| The tested working elements are too coarse or too low-order for the heterogeneous secondary field | Direct path retains 8-node cells; core refinement substantially reduced error | Strongest next diagnostic; P2 accuracy is untested |
| Finite-domain or mixed-boundary approximation remains significant | The original A/C and B/D extent comparisons failed | Still unresolved; preserve both extents in the P2 comparison |
| Our adapter mis-scaled or mis-signed all voltages | Literal reference and homogeneous units checks pass; extraction follows the library's direct branch | Evidence argues against a global convention error; not an exhaustive native audit |
| The primary-mesh diagnostic caused the voltage discrepancy | The query occurs after voltage calculation | Not an explanation for the recorded field error; remove the unnecessary query |
| The Python version string identifies the compiled core | Reported revision matches OpenSubsurface Git history | Rejected for this installation |

The [proposed P2 spec](../specs/ert-p2-contact-comparison.md) isolates polynomial refinement on fixed material cells. A reduction would support the discretization hypothesis, but an accuracy claim still requires the original strict gates and extent stability. No originality claim, sphere certification, or hardware decision follows from this source review.
