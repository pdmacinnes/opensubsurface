# Recommended research direction

Status: proposed hypothesis. No implementation or result.

## Recommendation

Study uncertainty-aware adaptive electrical resistivity tomography (ERT) for selected shallow three-dimensional electrical anomaly geometries.

The proposed acquisition policy chooses measurements to separate competing explanations. It accounts for uncertain electrode positions, acquisition errors, and underground background properties.

The policy must identify unresolved cases as well as successful distinctions.

## Research hypothesis

> For a specified family of shallow three-dimensional resistivity structures and realistic acquisition errors, sequential measurement selection targeting ambiguity between competing geometries can reach a defined inference accuracy using at most half the acquisition cost required by the strongest evaluated conventional or resolution-optimized design.

The factor of two is a proposed acceptance target. It is not an expected or demonstrated improvement.

The hypothesis makes no claim about arbitrary geology, material identity, or unlimited depth.

## Why start here

ERT has established forward physics, open-source solvers, and possible later open hardware validation. It provides a relatively accessible way to isolate information limits before adding elastic wave or radar complexity.

The team's initial contribution should be a verified acquisition method and measured comparison. A benchmark by itself would not establish the efficiency claim.

## Closest prior work

- [Wilkinson et al., 2012](https://core.ac.uk/download/pdf/2800724.pdf) address practical optimized ERT design.
- [Wilkinson et al., 2015](https://academic.oup.com/gji/article/203/1/755/586360) demonstrate adaptive laboratory ERT.
- [Strutz and Curtis, 2024](https://academic.oup.com/gji/article/236/3/1309/7492801) describe variational Bayesian geophysical experiment design.
- [The DC/IP study, 2024](https://doi.org/10.1016/j.jconhyd.2024.104452) evaluates Bayesian combined electrical survey design.
- [Han et al., 2025](https://doi.org/10.1029/2025WR040444) study spatial resolution and acquisition-time trade-offs.
- [Räsänen et al., 2026](https://onlinelibrary.wiley.com/doi/10.1002/nsg.70079) address electrode-position uncertainty.

Adaptivity, Bayesian inference, and nuisance modeling are not sufficient novelty claims. Before implementation, check for closer task-specific design methods and seek geophysical review of the draft protocol.

## Scientific claim boundary

The initial task concerns electrical geometry. It must distinguish detection, localization, shape recovery, and material identification.

A cavity and a solid inclusion with identical conductivity fields are indistinguishable to ideal DC observations. Any method claiming to identify their materials from those data fails the intended scientific standard.

A successful simulation comparison would justify physical validation. It would not establish field reliability or an operational mapping product.

## Decision after the first study

Proceed to a blinded physical experiment only if the gain survives strong baselines, nuisance errors, independent forward modeling, and held-out geology.

If surface data contain insufficient information, publish the limitation and investigate additional acquisition geometry. More complex reconstruction should not be the automatic response to an observability failure.

See the [first-experiment draft](first-experiment.md) for the proposed evaluation and [candidate alternatives](candidate-approaches.md).
