# Reproduce the pyGIMLi reflection discrepancy

This standalone example accompanies [pyGIMLi issue 979](https://github.com/gimli-org/pyGIMLi/issues/979). It reproduces the reported difference between two reflected measurement configurations in a vertical-contact model. The homogeneous control passes. The numerical cause remains unresolved.

Copy `reproduce.py` and `inputs.json` together to a directory outside OpenSubsurface. The script needs Python 3.12, NumPy, pyGIMLi, and pgcore. The recorded run uses NumPy 2.5.3, pyGIMLi 1.6.1, and pgcore 1.6.0. It does not import OpenSubsurface, SimPEG, SciPy, psutil, or Matplotlib. No new dependency was installed for this run. Apache 2.0 licensing applies through the [project license](../../LICENSE).

Validate the frozen inputs without importing pyGIMLi or calculating voltages:

```powershell
python reproduce.py --validate-only
```

Calculate the two states and save evidence to a fresh output path:

```powershell
python reproduce.py --output local-results.json
```

Keep all 64 sensors. The example extracts two ABMN rows but preserves the original C mesh, 23,328 material cells, 101,269 P2 nodes, boundary labels, and native direct calculation. It can still calculate all 64 source fields. Removing unused sensors or changing the mesh is a different experiment.

The script refuses an existing output path and validates the original axes, sensor order, current, measurement indices, resistivity states, and references. It assigns materials after P2 construction and checks the native topology and attributes. Each state uses a fresh operator, homogeneous analytical singularity removal, and direct `DataMap.data(scheme)` extraction. It supplies no exact-contact primary field or empirical correction.

H runs first. If it fails the `1e-12 V` reference and symmetry checks, C100 is skipped. The example reports `reproduced` only when C100 agrees with both historical numerical values within `1e-9 V` and its pair difference exceeds `1e-6 V`. These are reproduction criteria. The original survey's continuum-accuracy gates remain unchanged.

The script saves partial results before native work. Inconclusive execution exits with code 2, and exceptions return a failing process status. A completed non-reproduction exits normally with `not reproduced` in its output. Read that decision rather than inferring reproduction from exit status alone.

The [results](results/RESULTS.md) contain the executed voltages, console output, binary identities, checksums, and resources. Local execution used the existing project resource monitor around the copied script, with a 30-minute deadline and sampled 8 GiB process cap. The standalone script does not include that monitor. Use your own resource limits when executing elsewhere.

Review the [approved spec](../../specs/pygimli-reflection-reproduction.md) and [verification checkpoints](results/VERIFICATION.md). Unit tests and CI inspect inputs and saved evidence. They do not rerun these native contact calculations.
