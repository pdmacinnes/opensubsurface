# Draft public pyGIMLi review request

Status: Patrick approved publication. Posted as [pyGIMLi issue 979](https://github.com/gimli-org/pyGIMLi/issues/979), and the published title and message were verified against this draft. External technical review is pending.

## Proposed title

Question: y-reflection consistency for direct 3D DCSR contact calculations with P2 cells

## Proposed message

We are validating a small independent open-source DC modelling study against an exact vertical-contact reference. We would appreciate guidance on the supported direct calculation path and the best diagnostic for a reflection discrepancy. We have not identified a native-library bug or established its cause.

The material model is a flat half-space with an infinite contact at `x=0`. Left resistivity is 100 ohm m and right resistivity is 10,000 ohm m. Sources are mathematical surface points, current is 0.001 A, and measurements are signed ABMN volts. We use symmetric regular/graded axes and explicit P2 refinement of the original hexahedral cells, assigning resistivities after refinement. The outer boundaries use the existing mixed markers and the surface uses Neumann markers.

The calculation is `ERTModelling(sr=True)`, `setMesh(mesh, ignoreRegionManager=True)`, `mapERTModel(resistivity, 0)`, `calculate(DataMap)`, then `DataMap.data(scheme) * current`. No exact contact field is supplied to the native operator. Our distribution versions are pyGIMLi 1.6.1 and pgcore 1.6.0; the native core reports `libgimli-v1.6.0-4-g9076db0e`. Binary and installed-source hashes are recorded. The Python `__version__` in this workspace can resolve the enclosing project checkout, so we do not use it as native provenance.

One concrete pair has source/receiver coordinates:

| Electrode | First configuration, meters | Reflected configuration, meters |
| --- | --- | --- |
| A | `(-1.5,-4.5,0)` | `(-1.5,4.5,0)` |
| B | `(1.5,1.5,0)` | `(1.5,-1.5,0)` |
| M | `(7.5,1.5,0)` | `(7.5,-1.5,0)` |
| N | `(10.5,7.5,0)` | `(10.5,-7.5,0)` |

The exact contact reference is `-0.06000386265259415 V` for both configurations. On the 128 m P2 domain, native responses are `-0.05981245281773522 V` and `-0.059951241221804834 V`, differing by approximately 138.788 microvolt. The 64 m result has a similar difference. The homogeneous control agrees between the same pair near machine precision.

The x/y axis arrays are reflection symmetric. Cell correspondence, interface alignment, exact electrode nodes, and explicit core material attributes were checked. This pair does not exchange source and receiver roles or reverse within-pair orientation when matched. We found three reflection pairs in the already-computed manifest; all are included in the saved-data audit.

Could you advise which checks would distinguish primary-load construction, element/boundary assembly, electrode projection, reference constraints, and solver accuracy on this direct path? Are there supported diagnostics for actual reference constraints, reciprocity, or the separately assembled volume/boundary operators? Should we be using a different existing formulation for this benchmark before attempting further refinement?

The [public project](https://github.com/pdmacinnes/opensubsurface) contains the pinned environment, full source, original state arrays, topology/material checks, checksum provenance, analytical reference, and report commands. The relevant paths are:

- `experiments/ert-p2-contact-comparison/results/2026-10-09/`
- `research/contact-reference.md`
- `research/error-budget-boundary-review.md`
- `research/reproduce-boundary-review.md`
- `src/opensubsurface/p2_contact.py`

The benchmark code and audit are currently on the project's review branches, not all merged into its default branch. The audit branch is `docs/boundary-error-budget-review` and the executed P2 branch is `feat/p2-contact-comparison`. We can provide a smaller native reproduction if that would help. This request seeks formulation/diagnostic guidance; it does not claim accurate subsurface mapping or a new method.
