# Recomputed numerical evidence

Scientific outcome: **inconclusive**.

These tables are generated from the published raw voltages and mesh metadata. All discrepancies use the original analytic-background noise scale. RMS <= 0.1 and maximum <= 0.25 are required.

## Homogeneous reference

| Configuration | RMS | Maximum | Cells | Peak GiB | Equation residual | Gate |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| baseline-tree | 2.0828 | 36.31 | 25264 | 0.253 | 9.83e-11 | False |
| independent-pygimli-h15 | 2.63998e-13 | 2.66454e-12 | 13500 | 0.754 | not exposed by adapter | True |
| tensor-h025-e64-g15 | 0.633404 | 6.58603 | 821516 | 1.284 | 9.97e-11 | False |
| tensor-h05-e128-g15 | 1.27403 | 23.9384 | 171500 | 0.647 | 1e-10 | False |
| tensor-h05-e64-g12 | 0.865622 | 23.5291 | 256000 | 0.903 | 9.21e-11 | False |
| tensor-h05-e64-g15-c24 | 0.878234 | 23.4308 | 740772 | 1.171 | 9.99e-11 | False |
| tensor-h05-e64-g15 | 1.11164 | 23.8495 | 143748 | 0.564 | 9.53e-11 | False |
| tree-balls003125-r16-remote2 | 0.226194 | 2.16656 | 2003184 | 7.301 | 1e-10 | False |
| tree-balls003125-remote2 | 0.635038 | 6.21077 | 426588 | 1.768 | 9.85e-11 | False |
| tree-balls00625-r16-remote2 | 0.226119 | 2.16642 | 1392112 | 5.185 | 9.72e-11 | False |
| tree-remote2 | 1.6 | 38.4774 | 68804 | 0.480 | 4.9e-11 | False |

## Inclusion mesh changes

These are numerical convergence comparisons, not geometry-discrimination scores. Agreement between two meshes does not alone prove accuracy.

| First mesh | Second mesh | Existing geometry | RMS | Maximum | Gate |
| --- | --- | --- | ---: | ---: | --- |
| pygimli-inclusions-h075 | pygimli-inclusions-h075-core6 | h1-ba32b0c77ef15679 | 0.0126318 | 0.169654 | True |
| pygimli-inclusions-h075 | pygimli-inclusions-h075-core6 | h1-f8fa2489359b0830 | 0.00204131 | 0.0251598 | True |
| pygimli-inclusions-h075 | pygimli-inclusions-h075-core6 | h2-83c81c35bdbb7ddf | 0.000917755 | 0.0115812 | True |
| pygimli-inclusions-h075 | pygimli-inclusions-h075-core6 | h2-996eccf7a825f5aa | 0.00641941 | 0.0915745 | True |
| pygimli-inclusions-h075-core6 | pygimli-inclusions-h05-core6 | h1-ba32b0c77ef15679 | 0.793945 | 10.6302 | False |
| pygimli-inclusions-h075-core6 | pygimli-inclusions-h05-core6 | h1-f8fa2489359b0830 | 0.0372074 | 0.720642 | False |
| pygimli-inclusions-h075-core6 | pygimli-inclusions-h05-core6 | h2-83c81c35bdbb7ddf | 0.115544 | 1.86942 | False |
| pygimli-inclusions-h075-core6 | pygimli-inclusions-h05-core6 | h2-996eccf7a825f5aa | 1.62691 | 24.3526 | False |
| fitted-s24-r12-v005 | fitted-s48-r24-v0025 | h1-ba32b0c77ef15679 | 0.243568 | 3.87011 | False |
| fitted-s24-r12-v005 | fitted-s48-r24-v0025 | h1-f8fa2489359b0830 | 0.0553916 | 0.613437 | False |
| fitted-s24-r12-v005 | fitted-s48-r24-v0025 | h2-83c81c35bdbb7ddf | 0.0448359 | 0.651347 | False |
| fitted-s24-r12-v005 | fitted-s48-r24-v0025 | h2-996eccf7a825f5aa | 0.172111 | 2.63885 | False |
| fitted-s48-r24-v0025 | fitted-s48-r24-v001 | h1-ba32b0c77ef15679 | 0.171373 | 3.80014 | False |
| fitted-s48-r24-v0025 | fitted-s48-r24-v001 | h1-f8fa2489359b0830 | 0.0470071 | 0.537133 | False |
| fitted-s48-r24-v0025 | fitted-s48-r24-v001 | h2-83c81c35bdbb7ddf | 0.0386381 | 0.489892 | False |
| fitted-s48-r24-v0025 | fitted-s48-r24-v001 | h2-996eccf7a825f5aa | 0.192896 | 2.80936 | False |
| fitted-s48-r24-v0025 | fitted-s64-r32-v0025 | h1-ba32b0c77ef15679 | 0.195503 | 5.4209 | False |
| fitted-s48-r24-v0025 | fitted-s64-r32-v0025 | h1-f8fa2489359b0830 | 0.0559374 | 1.05865 | False |
| fitted-s48-r24-v0025 | fitted-s64-r32-v0025 | h2-83c81c35bdbb7ddf | 0.0454067 | 0.949031 | False |
| fitted-s48-r24-v0025 | fitted-s64-r32-v0025 | h2-996eccf7a825f5aa | 0.208702 | 4.08805 | False |

## Represented body volumes

| Mesh | Geometry | Nominal m3 | Represented m3 | Relative error |
| --- | --- | ---: | ---: | ---: |
| fitted-s24-r12-v005 | h1-ba32b0c77ef15679 | 14.137167 | 13.738114 | -2.823% |
| fitted-s24-r12-v005 | h1-f8fa2489359b0830 | 14.137167 | 13.738114 | -2.823% |
| fitted-s24-r12-v005 | h2-996eccf7a825f5aa | 14.137167 | 13.738114 | -2.823% |
| fitted-s24-r12-v005 | h2-83c81c35bdbb7ddf | 14.137167 | 13.737322 | -2.828% |
| fitted-s48-r24-v001 | h1-ba32b0c77ef15679 | 14.137167 | 14.036529 | -0.712% |
| fitted-s48-r24-v001 | h1-f8fa2489359b0830 | 14.137167 | 14.036529 | -0.712% |
| fitted-s48-r24-v001 | h2-996eccf7a825f5aa | 14.137167 | 14.036529 | -0.712% |
| fitted-s48-r24-v001 | h2-83c81c35bdbb7ddf | 14.137167 | 14.036529 | -0.712% |
| fitted-s48-r24-v0025 | h1-ba32b0c77ef15679 | 14.137167 | 14.036529 | -0.712% |
| fitted-s48-r24-v0025 | h1-f8fa2489359b0830 | 14.137167 | 14.036529 | -0.712% |
| fitted-s48-r24-v0025 | h2-996eccf7a825f5aa | 14.137167 | 14.036529 | -0.712% |
| fitted-s48-r24-v0025 | h2-83c81c35bdbb7ddf | 14.137167 | 14.036529 | -0.712% |
| fitted-s64-r32-v0025 | h1-ba32b0c77ef15679 | 14.137167 | 14.080473 | -0.401% |
| fitted-s64-r32-v0025 | h1-f8fa2489359b0830 | 14.137167 | 14.08048 | -0.401% |
| fitted-s64-r32-v0025 | h2-996eccf7a825f5aa | 14.137167 | 14.080486 | -0.401% |
| fitted-s64-r32-v0025 | h2-83c81c35bdbb7ddf | 14.137167 | 14.080486 | -0.401% |
| pygimli-inclusions-h05-core6 | h1-ba32b0c77ef15679 | 14.137167 | 17 | 20.250% |
| pygimli-inclusions-h05-core6 | h1-f8fa2489359b0830 | 14.137167 | 17 | 20.250% |
| pygimli-inclusions-h05-core6 | h2-996eccf7a825f5aa | 14.137167 | 14 | -0.970% |
| pygimli-inclusions-h05-core6 | h2-83c81c35bdbb7ddf | 14.137167 | 14 | -0.970% |
| pygimli-inclusions-h075-core6 | h1-ba32b0c77ef15679 | 14.137167 | 13.5 | -4.507% |
| pygimli-inclusions-h075-core6 | h1-f8fa2489359b0830 | 14.137167 | 16.875 | 19.366% |
| pygimli-inclusions-h075-core6 | h2-996eccf7a825f5aa | 14.137167 | 6.75 | -52.254% |
| pygimli-inclusions-h075-core6 | h2-83c81c35bdbb7ddf | 14.137167 | 10.125 | -28.380% |
| pygimli-inclusions-h075 | h1-ba32b0c77ef15679 | 14.137167 | 13.5 | -4.507% |
| pygimli-inclusions-h075 | h1-f8fa2489359b0830 | 14.137167 | 16.875 | 19.366% |
| pygimli-inclusions-h075 | h2-996eccf7a825f5aa | 14.137167 | 6.75 | -52.254% |
| pygimli-inclusions-h075 | h2-83c81c35bdbb7ddf | 14.137167 | 10.125 | -28.380% |

## Resources

Accounted worker time including the retry reserve: 3499.45 s. Maximum recorded process peak: 7.301 GiB. The ledger sums overlapping probe times, so it is conservative. These are CPU runs; no GPU speedup is claimed.
