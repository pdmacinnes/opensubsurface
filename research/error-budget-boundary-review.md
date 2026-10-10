# Error-budget and boundary-formulation review

Review date: October 9, 2026, America/Denver. This is an assistant-prepared literature and saved-data audit, not external professional peer review. No person was contacted, no new native voltage solve was run, and no acceptance criterion was changed.

**Recommendation:** stop adding mesh sweeps until the discrete source/boundary formulation and its symmetry properties have been checked. The evidence supports both an unusually demanding error budget and an unresolved numerical consistency issue. It does not establish a physical observability limit.

Read the [external-review brief](external-geophysical-review-brief.md), [reproduction recipe](reproduce-boundary-review.md), and [derived data](boundary-error-budget-review/2026-10-09/). The original [P2 decisions](../experiments/ert-p2-contact-comparison/results/2026-10-09/RESULTS.md) remain unchanged.

## Established saved-data findings

The premise under examination is: **further local resolution or polynomial-order refinement is the decisive lever for passing the frozen all-datum gates**. The linear/fine-core/P2 studies did not establish that premise. The census below identifies which measurement classes carry the normalized error before proposing another correction.

All fundamental P2 input/output checksums were verified before the analysis. A background-null datum is defined here by `abs(V_H) <= 1e-14` V. This post-hoc grouping does not exclude any observation.

There are 32 background-null configurations among 4,096 observations, approximately 0.78%. They contribute 64.5-65.2% of P2's total squared error under the frozen tolerance weights, across both extents and contrasts. In C-P2/C100, the split-source/right-receiver class accounts for 87.2% of that total. The complete role census is published; canonicalization makes some role classes empty, so these counts must not be interpreted as electrode malfunction or independent causal evidence.

| P2 case | Relative L2 voltage error | Maximum absolute voltage error | Null-class share of frozen weighted squared error |
| --- | ---: | ---: | ---: |
| A, C10 | 0.7119% | 1.535 mV | 64.51% |
| A, C100 | 0.8899% | 18.403 mV | 64.94% |
| C, C10 | 0.7111% | 1.533 mV | 64.82% |
| C, C100 | 0.8886% | 18.385 mV | 65.22% |

Relative L2 means `norm(V_numeric - V_reference) / norm(V_reference)` over all observations. It is not a maximum relative error and cannot certify weak channels. The maximum absolute error is also distinct from the datum with maximum frozen normalized error.

### The tolerance scale is a design choice, not measured instrument noise

The frozen scale is `hypot(0.01 * abs(V_H), 1e-6)` V. Where its relative component dominates, RMS 0.1 corresponds roughly to a 0.1% background-relative numerical budget. A zero-background datum has a maximum allowed absolute discrepancy of 0.25 microvolt.

The worst frozen P2 datum, row 3839, has a 1 microvolt scale. Its contact reference is 21.251 mV in C10 and 254.587 mV in C100. Applying the same relative/floor formula to those contact reference values would produce scales approximately 212.5 and 2545.9 times larger. That alternative is a sensitivity diagnostic, not a replacement gate or a calibrated noise model.

Even that diagnostic does not certify the results. For C-P2, its normalized RMS/maximum are approximately 11.98/737.31 in C10 and 26.45/1000.09 in C100. Different near-zero-contact channels become heavily weighted. Rescaling does not remove the observed numerical error.

[Zhou and Greenhalgh (2001)](https://doi.org/10.1046/j.0956-540x.2001.01412.x) report model-specific finite-element accuracy comparisons using percentage errors. Those results illustrate a different evaluation convention, not a transferable guarantee for our 4,096 signed voltages. Our aggregate errors being below 1% is compatible with failing stringent weak-channel requirements.

The appropriate numerical tolerance for the original one-body/two-body decision has not yet been justified against validated target-response separations or calibrated acquisition noise. The geometry/nuisance bank was not completed. Keep the failed historical decisions, and define any future task-linked budget before another experiment.

## Verified native boundary structure

The reviewed source is pinned to the native core's reported revision [9076db0efdadad36b38554858b832ff6b1a800cd](https://github.com/gimli-org/pyGIMLi/blob/9076db0efdadad36b38554858b832ff6b1a800cd/core/src/bert/dcfemmodelling.cpp). The relevant locations are `mixedBoundaryCondition`, the mixed-boundary assembler, `searchElectrodes_`, `preCalculate`, and `calculateK`.

For valid symmetric surface electrodes, the shared electrode-center position is `(0,0,0)`. At zero wavenumber, its mirror is identical. The coefficient at each boundary-facet center simplifies to

$$
\alpha_F = \frac{|\mathbf n_F\cdot(\mathbf p_F-\mathbf c)|}{|\mathbf p_F-\mathbf c|^2}.
$$

The center is inferred from the source for the declared valid matched sensor set; the original native runs did not separately log that value. This assumption is retained explicitly in the analytical probes.

The assembler evaluates that coefficient once at the facet center, multiplies the face mass matrix by `alpha_F / rho_boundary`, and uses the adjacent cell's resistivity. P2 changes the basis but does not change this coefficient into a spatially varying quadrature evaluation.

The primary-derived right-hand side also includes the boundary operator. The discrete identities, away from special constrained rows, are

`b_secondary = S1 * u_primary / rho_source - S * u_primary`,

`S * u_total = S1 * g_unit`,

where the unit-resistivity primary is `g_unit` and `u_primary = rho_source * g_unit` in the source's numerical unit convention. The second relation follows by adding the primary back after the secondary solve. This is not simply a homogeneous zero-Robin condition on the total potential.

## Continuous analogue and its limits

Let `g_ref` be the unit-current homogeneous Green function for reference conductivity `sigma_ref = 1 S/m`. A formal continuous analogue of that shared-operator boundary structure is

$$
\sigma(\partial_n G+\alpha_F G)
=\sigma_{ref}(\partial_n g_{ref}+\alpha_F g_{ref}).
$$

The interpretation uses the facetwise coefficient and the primary-derived forcing. It does not replace the actual discrete operators, source-node treatment, quadrature, or calibration constraints.

This identity explains the limited homogeneous control. If the entire domain has conductivity `sigma_h`, then `G = (sigma_ref/sigma_h) g_ref` satisfies the identity for any coefficient. Homogeneous agreement does not independently validate the heterogeneous boundary data.

[Li and Spitzer (2002)](https://doi.org/10.1046/j.1365-246X.2002.01819.x) discuss how heterogeneous backgrounds and the primary formulation affect boundary accuracy. [Zhang et al. (2016)](https://doi.org/10.6038/cjg20160927) describe the source-position dependence of mixed-boundary matrices and methods that move boundary terms into the right-hand side for repeated sources. These are established numerical issues and prior art, not a new OpenSubsurface technique.

### Analytical boundary probes

We evaluated the exact contact Green function and its gradient at the saved A/C outer-facet centers. The diagnostic residual is

`r_F = sigma_F * (n.dot(grad(G_contact)) + alpha_F * G_contact) - sigma_ref * (n.dot(grad(g_ref)) + alpha_F * g_ref)`.

We report the midpoint sum of `area_F * abs(r_F)` across the five outer faces, normalized to unit injected current. It is a boundary-data consistency diagnostic. It is not actual leaked current, a voltage error, a rigorous error bound, an algebraic residual, or an exact weak residual.

| Mesh and state | Median absolute mismatch measure over 64 sources | Maximum measure |
| --- | ---: | ---: |
| A, H | 9.38e-17 | 1.00e-16 |
| A, C10 | 0.05739 | 0.08414 |
| A, C100 | 0.06875 | 0.10080 |
| C, H | 9.33e-17 | 9.81e-17 |
| C, C10 | 0.02980 | 0.04468 |
| C, C100 | 0.03570 | 0.05352 |

The homogeneous negative control vanishes numerically. The exact heterogeneous infinite-domain response does not satisfy this formal finite-boundary analogue exactly at the sampled locations. The decrease with extent supports investigating truncation/formulation mismatch. It does not prove how much of the electrode-voltage error originates there.

## A stronger self-consistency warning from saved pairs

The contact material model is invariant under translation along y and reflection `y -> -y`. We searched only the existing manifest for transformed pairs. No new configuration was simulated, and all matching exact reference values agree after orientation correction.

There are eight translated pairs and three reflected pairs. None of the three reflected matches exchanges source and receiver roles after canonicalization, so their discrepancies cannot be explained solely by a reciprocal-role swap. The saved x/y axes are reflection symmetric.

| P2 invariant and contrast | Maximum discrepancy at A | Maximum discrepancy at C |
| --- | ---: | ---: |
| y translation, C10 | 2.696 microvolt | 2.609 microvolt |
| y translation, C100 | 36.362 microvolt | 35.371 microvolt |
| y reflection, C10 | 11.563 microvolt | 11.564 microvolt |
| y reflection, C100 | 138.783 microvolt | 138.788 microvolt |

Homogeneous matched-pair discrepancies are near machine precision. Reflection should also be respected by the declared symmetric finite box, material assignment, and shared-center coefficient. The heterogeneous reflection discrepancy therefore prevents blaming the continuous outer-boundary approximation alone. Discrete assembly, primary-load construction, electrode projection, solver accuracy, or unrecorded constraints need inspection. The three-pair sample is a post-hoc diagnostic, not a comprehensive invariant test or identification of one root cause.

## Decision and suggested next investigation

Do not average, symmetrize, or empirically correct the saved voltages. Do not exclude the 32 background-null channels to manufacture a pass. Keep the historical thresholds and decisions intact.

The next useful technical step would be a separately scoped operator-consistency audit: inspect volume and boundary contributions independently, use the known smooth secondary contact field to avoid the point-source singularity, and verify symmetry/reciprocity and actual reference constraints. API access and native details need checking before implementation. Assembly diagnostics or oracle boundary controls would be numerical debugging evidence, not a deployable mapping result.

An external geophysicist should review the matrix derivation and target-linked numerical budget before that step. The [brief](external-geophysical-review-brief.md) lists the exact questions and files. No external reviewer has endorsed this audit.

Established evidence consists of the saved-array statistics, matched-pair discrepancies, and inspected source structure. The continuous boundary analogue is a mathematical interpretation with stated limits. Attribution of the dominant error and transfer to accurate sphere mapping remain hypotheses.
