# Recomputed contact benchmark evidence

Scientific outcome: **inconclusive**.

All errors use the original fixed homogeneous tolerance scale. RMS <= 0.1 and maximum <= 0.25 are required.

| Mesh | State | Status | RMS | Maximum | Pass |
| --- | --- | --- | ---: | ---: | --- |
| A | H | completed | 2.7104660057921636e-13 | 2.6645352591003757e-12 | True |
| A | C10 | completed | 52.28800622862042 | 2827.8487381299715 | False |
| A | C100 | completed | 625.9219713764342 | 33878.1878528443 | False |
| B | H | completed | 8.055111212881201e-13 | 5.386284067043973e-12 | True |
| B | C10 | completed | 10.449837422026853 | 553.9451623733996 | False |
| B | C100 | completed | 125.03502983233307 | 6636.372737344132 | False |
| C | H | completed | 2.7397519269560853e-13 | 2.7755575615628918e-12 | True |
| C | C10 | completed | 52.31299144664358 | 2827.905258244005 | False |
| C | C100 | completed | 626.1958571103868 | 33878.86497500242 | False |
| D | H | completed | 8.009203031034379e-13 | 5.042847119765518e-12 | True |
| D | C10 | completed | 10.441376738871682 | 554.0018235310023 | False |
| D | C100 | completed | 124.94258911376069 | 6637.051549232359 | False |

| First | Second | Changed factor | State | RMS | Maximum | Pass |
| --- | --- | --- | --- | ---: | ---: | --- |
| A | B | core resolution | H | 7.127e-13 | 5.8694e-12 | True |
| A | B | core resolution | C10 | 42.0029 | 2273.9 | False |
| A | B | core resolution | C100 | 502.776 | 27241.8 | False |
| C | D | core resolution | H | 7.04975e-13 | 5.8694e-12 | True |
| C | D | core resolution | C10 | 42.0029 | 2273.9 | False |
| C | D | core resolution | C100 | 502.775 | 27241.8 | False |
| A | C | extent | H | 7.58767e-14 | 1.75683e-12 | True |
| A | C | extent | C10 | 0.993295 | 11.2436 | False |
| A | C | extent | C100 | 11.5137 | 129.747 | False |
| B | D | extent | H | 9.03218e-14 | 1.25563e-12 | True |
| B | D | extent | C10 | 0.994396 | 11.2507 | False |
| B | D | extent | C100 | 11.5264 | 129.829 | False |

Native state solves attempted: 12. Accounted worker time: 650.713 s, including 600 s development allowance. Peak recorded process memory: 3.695 GiB.

Single-run CPU resource observations describe this study. They do not establish a repeatable speedup or validate sphere responses.
