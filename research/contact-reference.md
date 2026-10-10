# Exact vertical-contact reference

Status: reviewed mathematical definition, now implemented and checked in the [approved contact study](../experiments/ert-contact-benchmark/README.md). The analytical checks pass; all native heterogeneous accuracy checks fail. This note describes the reference rather than claiming accurate native voltages.

The original image solution appears in Van Nostrand and Cook, [Interpretation of resistivity data](https://pubs.usgs.gov/pp/0499/report.pdf), USGS Professional Paper 499, printed pages 52-53, equations 21-23. The notation below places the source in either medium and uses conductivity rather than resistivity.

## Model and Green function

The ground occupies `z < 0` with an insulating surface at `z = 0`. The ideal contact is `x = 0`, extending infinitely along `y` and depth. Conductivity is positive and constant within each side, with no interface contact resistance. Potential vanishes at infinity.

For a surface source `s = (x_s, y_s, 0)` away from the contact, let `sigma_s` denote its medium's conductivity and `sigma_o` the other medium's conductivity. The image is `s* = (-x_s, y_s, 0)`. Set `r = |p-s|`, `r* = |p-s*|`, and

$$
R_s = \frac{\sigma_s-\sigma_o}{\sigma_s+\sigma_o}.
$$

For a receiver in the same medium as the source, the Green function in volts per ampere is

$$
G(p,s) = \frac{1}{2\pi\sigma_s}
\left(\frac{1}{r}+\frac{R_s}{r^*}\right).
$$

For a receiver in the other medium,

$$
G(p,s) = \frac{1}{\pi(\sigma_s+\sigma_o)r}.
$$

For a source current `I`, the pole potential is `I G`. The reflection factor is equivalently `(rho_o-rho_s)/(rho_o+rho_s)`. For the original signed dipole measurement,

$$
V_{ABMN}=I\,[G(M,A)-G(M,B)-G(N,A)+G(N,B)].
$$

There is one factor of current in this expression. A zero dipole voltage is a valid result. No apparent-resistivity division or absolute-value conversion belongs in this voltage reference.

The formulas also evaluate points below the surface. Contact limits are defined by taking either one-sided expression; a source exactly on the contact needs a separate treatment and is excluded.

## Independent mathematical checks

At the contact, `r = r*`. The same-side coefficient becomes `1/[pi (sigma_s+sigma_o)]`, matching the transmitted potential.

For a source on the left at `x_s = -a`, the derivative at `x = 0` from the left is

$$
\partial_x G_L = -\frac{a(1-R_L)}{2\pi\sigma_L r^3}.
$$

From the right it is

$$
\partial_x G_R = -\frac{a}{\pi(\sigma_L+\sigma_R)r^3}.
$$

Since `1-R_L = 2 sigma_R/(sigma_L+sigma_R)`, the normal currents `-sigma_L partial_x G_L` and `-sigma_R partial_x G_R` agree. A reflected source on the right gives the corresponding identity with sides exchanged.

The surface normal derivative is zero away from a source, because the distance terms depend on `z^2`. Near a source, the singular term has coefficient `1/(2 pi sigma_s)` and injects unit current into the ground hemisphere; its image contribution is locally nonsingular. The fields are harmonic away from sources and interfaces and decay at infinity. These properties identify the intended boundary-value problem.

If the conductivities are equal, `R_s = 0` and both branches reduce to the homogeneous half-space Green function. Reciprocity holds because same-side image distances are symmetric and the cross-contact coefficient is symmetric in the two conductivities. These checks are independent physical identities, not agreement with a second run of the same mesh solver.

## Literal reference checks for implementation review

These auxiliary points check the formula only. They are not additions to the native solver's frozen measurement manifest.

Use `rho_L = 100 ohm m`, `rho_R = 1000 ohm m`, and `I = 0.001 A`. Put `A = (-3,0,0)`, `B = (3,0,0)`, `M = (-1,0,0)`, and `N = (1,0,0)`.

| Quantity | Expected volts |
| --- | --- |
| Pole potential from A at M | `31 / (880 pi)` |
| Pole potential from A at N | `1 / (44 pi)` |
| Pole potential from B at M | `1 / (44 pi)` |
| Pole potential from B at N | `13 / (88 pi)` |
| Pole potential from A at `(0,0,0)`, using either contact limit | `1 / (33 pi)` |
| Signed ABMN voltage | `11 / (80 pi)` |

The proposed implementation must verify these values, equal-conductivity reduction, reciprocity, and the interface identities before using this reference to judge native voltages. A comparison fails if source/receiver coincidence, invalid conductivity, wrong units, or unsupported geometry is silently accepted.
