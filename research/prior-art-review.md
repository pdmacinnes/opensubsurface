# Focused prior-art review for adaptive ERT

Reviewed October 8, 2026. Status: literature findings and research judgment. No project experiment has been run.

## Conclusion

Originality is unconfirmed. Target-specific Bayesian electrical survey design and Bayesian design with nuisance uncertainty already exist.

The proposed contribution cannot be described as inventing adaptive ERT, task-specific design, uncertainty-aware design, or electrode-response reuse. A future contribution needs a specific method and a measured advantage over these precedents.

The next proposed work is an [observability pilot specification](../specs/ert-observability-pilot.md). It tests whether the initial geometry task is informative before investing in an acquisition policy.

## Closest reviewed work

| Source | Reported scope | Implication for OpenSubsurface |
| --- | --- | --- |
| [Qiang et al., 2022](https://doi.org/10.1190/geo2021-0408.1) | Bayesian ERT design for a target of interest, including synthetic static and time-lapse tests | Target-specific expected information gain is existing prior art |
| [Bartuska, Espath, and Tempone, 2025](https://doi.org/10.1007/s11222-024-10544-z) | Bayesian design with marginalized nuisance uncertainty, including numerical EIT examples | Separating nuisance uncertainty from the quantity of interest is established |
| [Coles and Morgan, 2009](https://doi.org/10.1111/j.1365-246X.2009.04156.x) | Efficient determinant-based sequential design for linearized geophysical inverse problems | Efficient sequential selection is an established comparison |
| [Thibaut et al., 2022](https://doi.org/10.1029/2022WR033045) | Bayesian selection of well and geophysical observations for temperature monitoring | Prediction-focused design and ERT protocol comparisons already exist |
| [Karimi, Taghizadeh, and Heitzinger, 2021](https://doi.org/10.1016/j.cma.2020.113489) | Expected-information-gain EIT design, including frequency and electrode configuration | Boundary electrical sensing has related design methods outside geophysics |
| [Hyvönen et al., preprint 2023](https://arxiv.org/abs/2312.10383) | Offline and adaptive A-optimal electrode placement for head imaging | Adaptive electrode design with a complete-electrode model is also related prior art |

Medical and composite-material EIT are not the same acquisition geometry as surface geophysical ERT. Their design mathematics remains relevant.

Qiang et al. also use superposition to derive four-electrode responses from two-electrode responses. Reusing electrode-response calculations should be treated as established practice rather than a new algorithm.

The Qiang paper was reviewed through its author-uploaded manuscript. Publisher access was unavailable during this follow-up. The other sources were reviewed through their original article pages or author abstracts as available. No reproduced performance claim is made.

## A numerical improvement is not automatically an original contribution

The current evidence leaves several unresolved questions:

- Does targeting a binary geometry decision add value beyond existing Bayesian target-area design?
- Does that value remain after marginalizing location, contrast, and background uncertainty?
- Does it outperform existing methods at comparable acquisition time, rather than only at a fixed voltage-pair count?
- Does it survive nonmatching forward models and shapes outside the inference family?
- Can the method recognize an unresolved case without treating unsupported prior confidence as evidence?

These are proposed comparisons. The absence of an exact matching experiment in this search does not establish a literature gap.

## Why the first study should test observability

The broad experiment currently proposes learning an acquisition policy, modeling nuisance errors, evaluating uncertainty, and performing large three-dimensional comparisons. That is too much to establish whether the basic observations support the selected geometry question.

The first pilot should use a fixed candidate survey and a small explicit geometry family. It should compare response differences with declared noise and numerical error. It should then look for opposing explanations in a finite nuisance bank.

This sequence can reject an uninformative target before algorithm development. It cannot prove practical field detectability, global uniqueness, or acquisition savings.

## Conditions for a later novelty claim

A later adaptive study must include a target-specific Bayesian baseline and distinguish its mathematical objective from established expected-information-gain methods.

If closest baseline reproduction is blocked by unavailable details or licensing, document that limitation. Do not replace it with a weak approximation and claim superiority to the original method.

A twofold improvement over conventional arrays alone would be insufficient evidence of originality if stronger optimized designs perform similarly.

The pilot may instead support the alternative direction of changing acquisition geometry. A negative result is a research finding only after numerical and physical assumptions pass verification.

## Search scope and limits

Queries covered electrical resistivity model discrimination, target-specific ERT survey design, Bayesian EIT design, nuisance uncertainty, and sequential geophysical design. Follow-up tracing used the references in Thibaut et al. and the original Qiang manuscript.

This is a focused follow-up, not a systematic review. Full reproduction of the closest methods and external geophysical review remain outstanding.
