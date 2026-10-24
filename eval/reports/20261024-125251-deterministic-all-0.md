# Unit eval

**Run** deterministic, skill `skill` at 6ec9cf5, content fde9d1b38713, model none

- split all, 1 run(s), started 2026-10-24 12:52, cost none
- 814 units, 814 predictions, 0 unanswered, 0 confidential units counted, 0 confidential units skipped

Human ceiling: no blind re-label yet. Run `eval/label.py --audit`.

## gold

### gold · none · overall (15 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 6 | FN 9 | sensitivity 0.400 (6/15) [0.198, 0.643] |
| **labelled not** | FP 0 | TN 0 | specificity n/a (0/0) |
|  | precision 1.000 (6/6) [0.610, 1.000] | NPV 0.000 (0/9) [0.000, 0.299] | accuracy 0.400 (6/15) [0.198, 0.643] |

prevalence 1.000 (15/15) [0.796, 1.000] · F1 0.571 (12/21) [0.333, 0.800] · balanced accuracy n/a · MCC n/a

### gold · none · language markdown (2 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 2 | FN 0 | sensitivity 1.000 (2/2) [0.342, 1.000] |
| **labelled not** | FP 0 | TN 0 | specificity n/a (0/0) |
|  | precision 1.000 (2/2) [0.342, 1.000] | NPV n/a (0/0) | accuracy 1.000 (2/2) [0.342, 1.000] |

prevalence 1.000 (2/2) [0.342, 1.000] · F1 1.000 (4/4) [1.000, 1.000] · balanced accuracy n/a · MCC n/a

### gold · none · language python (13 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 4 | FN 9 | sensitivity 0.308 (4/13) [0.127, 0.576] |
| **labelled not** | FP 0 | TN 0 | specificity n/a (0/0) |
|  | precision 1.000 (4/4) [0.510, 1.000] | NPV 0.000 (0/9) [0.000, 0.299] | accuracy 0.308 (4/13) [0.127, 0.576] |

prevalence 1.000 (13/13) [0.772, 1.000] · F1 0.471 (8/17) [0.143, 0.762] · balanced accuracy n/a · MCC n/a

### gold · none · rule NAR017 (326 units)

|  | predicted NAR017 | predicted not |  |
|---|---|---|---|
| **labelled NAR017** | TP 29 | FN 2 | sensitivity 0.935 (29/31) [0.793, 0.982] |
| **labelled not** | FP 0 | TN 295 | specificity 1.000 (295/295) [0.987, 1.000] |
|  | precision 1.000 (29/29) [0.883, 1.000] | NPV 0.993 (295/297) [0.976, 0.998] | accuracy 0.994 (324/326) [0.978, 0.998] |

prevalence 0.095 (31/326) [0.068, 0.132] · F1 0.967 (58/60) [0.917, 1.000] · balanced accuracy 0.968 [0.923, 1.000] · MCC 0.964 [0.912, 1.000]

### gold · snippet · overall (63 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 20 | FN 24 | sensitivity 0.455 (20/44) [0.317, 0.599] |
| **labelled not** | FP 4 | TN 15 | specificity 0.789 (15/19) [0.567, 0.915] |
|  | precision 0.833 (20/24) [0.641, 0.933] | NPV 0.385 (15/39) [0.249, 0.541] | accuracy 0.556 (35/63) [0.433, 0.672] |

prevalence 0.698 (44/63) [0.576, 0.798] · F1 0.588 (40/68) [0.441, 0.723] · balanced accuracy 0.622 [0.498, 0.738] · MCC 0.231 [-0.004, 0.445]

### gold · snippet · language python (63 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 20 | FN 24 | sensitivity 0.455 (20/44) [0.317, 0.599] |
| **labelled not** | FP 4 | TN 15 | specificity 0.789 (15/19) [0.567, 0.915] |
|  | precision 0.833 (20/24) [0.641, 0.933] | NPV 0.385 (15/39) [0.249, 0.541] | accuracy 0.556 (35/63) [0.433, 0.672] |

prevalence 0.698 (44/63) [0.576, 0.798] · F1 0.588 (40/68) [0.444, 0.712] · balanced accuracy 0.622 [0.500, 0.735] · MCC 0.231 [0.000, 0.442]

## silver

### silver · snippet · overall (131 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 13 | FN 6 | sensitivity 0.684 (13/19) [0.460, 0.846] |
| **labelled not** | FP 94 | TN 18 | specificity 0.161 (18/112) [0.104, 0.240] |
|  | precision 0.121 (13/107) [0.072, 0.197] | NPV 0.750 (18/24) [0.551, 0.880] | accuracy 0.237 (31/131) [0.172, 0.316] |

prevalence 0.145 (19/131) [0.095, 0.215] · F1 0.206 (26/126) [0.113, 0.299] · balanced accuracy 0.422 [0.305, 0.537] · MCC -0.141 [-0.339, 0.064]

### silver · snippet · language python (131 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 13 | FN 6 | sensitivity 0.684 (13/19) [0.460, 0.846] |
| **labelled not** | FP 94 | TN 18 | specificity 0.161 (18/112) [0.104, 0.240] |
|  | precision 0.121 (13/107) [0.072, 0.197] | NPV 0.750 (18/24) [0.551, 0.880] | accuracy 0.237 (31/131) [0.172, 0.316] |

prevalence 0.145 (19/131) [0.095, 0.215] · F1 0.206 (26/126) [0.104, 0.301] · balanced accuracy 0.422 [0.301, 0.528] · MCC -0.141 [-0.352, 0.052]

### silver · snippet · rule F1 (131 units)

|  | predicted F1 | predicted not |  |
|---|---|---|---|
| **labelled F1** | TP 0 | FN 5 | sensitivity 0.000 (0/5) [0.000, 0.434] |
| **labelled not** | FP 0 | TN 126 | specificity 1.000 (126/126) [0.970, 1.000] |
|  | precision n/a (0/0) | NPV 0.962 (126/131) [0.914, 0.984] | accuracy 0.962 (126/131) [0.914, 0.984] |

prevalence 0.038 (5/131) [0.016, 0.086] · F1 0.000 (0/5) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · snippet · rule F2a (131 units)

|  | predicted F2a | predicted not |  |
|---|---|---|---|
| **labelled F2a** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 131 | specificity 1.000 (131/131) [0.972, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (131/131) [0.972, 1.000] | accuracy 1.000 (131/131) [0.972, 1.000] |

prevalence 0.000 (0/131) [0.000, 0.028] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

### silver · snippet · rule F2b (131 units)

|  | predicted F2b | predicted not |  |
|---|---|---|---|
| **labelled F2b** | TP 0 | FN 5 | sensitivity 0.000 (0/5) [0.000, 0.434] |
| **labelled not** | FP 0 | TN 126 | specificity 1.000 (126/126) [0.970, 1.000] |
|  | precision n/a (0/0) | NPV 0.962 (126/131) [0.914, 0.984] | accuracy 0.962 (126/131) [0.914, 0.984] |

prevalence 0.038 (5/131) [0.016, 0.086] · F1 0.000 (0/5) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · snippet · rule F3 (131 units)

|  | predicted F3 | predicted not |  |
|---|---|---|---|
| **labelled F3** | TP 0 | FN 2 | sensitivity 0.000 (0/2) [0.000, 0.658] |
| **labelled not** | FP 0 | TN 129 | specificity 1.000 (129/129) [0.971, 1.000] |
|  | precision n/a (0/0) | NPV 0.985 (129/131) [0.946, 0.996] | accuracy 0.985 (129/131) [0.946, 0.996] |

prevalence 0.015 (2/131) [0.004, 0.054] · F1 0.000 (0/2) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · snippet · rule F4 (131 units)

|  | predicted F4 | predicted not |  |
|---|---|---|---|
| **labelled F4** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 131 | specificity 1.000 (131/131) [0.972, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (131/131) [0.972, 1.000] | accuracy 1.000 (131/131) [0.972, 1.000] |

prevalence 0.000 (0/131) [0.000, 0.028] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

### silver · snippet · rule F5 (131 units)

|  | predicted F5 | predicted not |  |
|---|---|---|---|
| **labelled F5** | TP 0 | FN 4 | sensitivity 0.000 (0/4) [0.000, 0.490] |
| **labelled not** | FP 0 | TN 127 | specificity 1.000 (127/127) [0.971, 1.000] |
|  | precision n/a (0/0) | NPV 0.969 (127/131) [0.924, 0.988] | accuracy 0.969 (127/131) [0.924, 0.988] |

prevalence 0.031 (4/131) [0.012, 0.076] · F1 0.000 (0/4) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · snippet · rule F6 (131 units)

|  | predicted F6 | predicted not |  |
|---|---|---|---|
| **labelled F6** | TP 0 | FN 3 | sensitivity 0.000 (0/3) [0.000, 0.561] |
| **labelled not** | FP 0 | TN 128 | specificity 1.000 (128/128) [0.971, 1.000] |
|  | precision n/a (0/0) | NPV 0.977 (128/131) [0.935, 0.992] | accuracy 0.977 (128/131) [0.935, 0.992] |

prevalence 0.023 (3/131) [0.008, 0.065] · F1 0.000 (0/3) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · snippet · rule F7 (131 units)

|  | predicted F7 | predicted not |  |
|---|---|---|---|
| **labelled F7** | TP 0 | FN 18 | sensitivity 0.000 (0/18) [0.000, 0.176] |
| **labelled not** | FP 0 | TN 113 | specificity 1.000 (113/113) [0.967, 1.000] |
|  | precision n/a (0/0) | NPV 0.863 (113/131) [0.793, 0.911] | accuracy 0.863 (113/131) [0.793, 0.911] |

prevalence 0.137 (18/131) [0.089, 0.207] · F1 0.000 (0/18) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · snippet · rule F8 (131 units)

|  | predicted F8 | predicted not |  |
|---|---|---|---|
| **labelled F8** | TP 0 | FN 4 | sensitivity 0.000 (0/4) [0.000, 0.490] |
| **labelled not** | FP 0 | TN 127 | specificity 1.000 (127/127) [0.971, 1.000] |
|  | precision n/a (0/0) | NPV 0.969 (127/131) [0.924, 0.988] | accuracy 0.969 (127/131) [0.924, 0.988] |

prevalence 0.031 (4/131) [0.012, 0.076] · F1 0.000 (0/4) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · snippet · rule F9 (131 units)

|  | predicted F9 | predicted not |  |
|---|---|---|---|
| **labelled F9** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 131 | specificity 1.000 (131/131) [0.972, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (131/131) [0.972, 1.000] | accuracy 1.000 (131/131) [0.972, 1.000] |

prevalence 0.000 (0/131) [0.000, 0.028] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

### silver · window · overall (288 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 130 | FN 43 | sensitivity 0.751 (130/173) [0.682, 0.810] |
| **labelled not** | FP 45 | TN 70 | specificity 0.609 (70/115) [0.517, 0.693] |
|  | precision 0.743 (130/175) [0.673, 0.802] | NPV 0.619 (70/113) [0.527, 0.704] | accuracy 0.694 (200/288) [0.639, 0.745] |

prevalence 0.601 (173/288) [0.543, 0.656] · F1 0.747 (260/348) [0.691, 0.798] · balanced accuracy 0.680 [0.625, 0.736] · MCC 0.361 [0.252, 0.475]

### silver · window · language python (288 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 130 | FN 43 | sensitivity 0.751 (130/173) [0.682, 0.810] |
| **labelled not** | FP 45 | TN 70 | specificity 0.609 (70/115) [0.517, 0.693] |
|  | precision 0.743 (130/175) [0.673, 0.802] | NPV 0.619 (70/113) [0.527, 0.704] | accuracy 0.694 (200/288) [0.639, 0.745] |

prevalence 0.601 (173/288) [0.543, 0.656] · F1 0.747 (260/348) [0.693, 0.796] · balanced accuracy 0.680 [0.626, 0.736] · MCC 0.361 [0.253, 0.474]

### silver · window · rule F1 (288 units)

|  | predicted F1 | predicted not |  |
|---|---|---|---|
| **labelled F1** | TP 0 | FN 32 | sensitivity 0.000 (0/32) [0.000, 0.107] |
| **labelled not** | FP 0 | TN 256 | specificity 1.000 (256/256) [0.985, 1.000] |
|  | precision n/a (0/0) | NPV 0.889 (256/288) [0.847, 0.920] | accuracy 0.889 (256/288) [0.847, 0.920] |

prevalence 0.111 (32/288) [0.080, 0.153] · F1 0.000 (0/32) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · window · rule F2a (288 units)

|  | predicted F2a | predicted not |  |
|---|---|---|---|
| **labelled F2a** | TP 0 | FN 13 | sensitivity 0.000 (0/13) [0.000, 0.228] |
| **labelled not** | FP 0 | TN 275 | specificity 1.000 (275/275) [0.986, 1.000] |
|  | precision n/a (0/0) | NPV 0.955 (275/288) [0.924, 0.973] | accuracy 0.955 (275/288) [0.924, 0.973] |

prevalence 0.045 (13/288) [0.027, 0.076] · F1 0.000 (0/13) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · window · rule F2b (288 units)

|  | predicted F2b | predicted not |  |
|---|---|---|---|
| **labelled F2b** | TP 0 | FN 25 | sensitivity 0.000 (0/25) [0.000, 0.133] |
| **labelled not** | FP 0 | TN 263 | specificity 1.000 (263/263) [0.986, 1.000] |
|  | precision n/a (0/0) | NPV 0.913 (263/288) [0.875, 0.941] | accuracy 0.913 (263/288) [0.875, 0.941] |

prevalence 0.087 (25/288) [0.059, 0.125] · F1 0.000 (0/25) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · window · rule F3 (288 units)

|  | predicted F3 | predicted not |  |
|---|---|---|---|
| **labelled F3** | TP 0 | FN 33 | sensitivity 0.000 (0/33) [0.000, 0.104] |
| **labelled not** | FP 0 | TN 255 | specificity 1.000 (255/255) [0.985, 1.000] |
|  | precision n/a (0/0) | NPV 0.885 (255/288) [0.843, 0.917] | accuracy 0.885 (255/288) [0.843, 0.917] |

prevalence 0.115 (33/288) [0.083, 0.157] · F1 0.000 (0/33) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · window · rule F4 (288 units)

|  | predicted F4 | predicted not |  |
|---|---|---|---|
| **labelled F4** | TP 0 | FN 14 | sensitivity 0.000 (0/14) [0.000, 0.215] |
| **labelled not** | FP 0 | TN 274 | specificity 1.000 (274/274) [0.986, 1.000] |
|  | precision n/a (0/0) | NPV 0.951 (274/288) [0.920, 0.971] | accuracy 0.951 (274/288) [0.920, 0.971] |

prevalence 0.049 (14/288) [0.029, 0.080] · F1 0.000 (0/14) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · window · rule F5 (288 units)

|  | predicted F5 | predicted not |  |
|---|---|---|---|
| **labelled F5** | TP 0 | FN 98 | sensitivity 0.000 (0/98) [0.000, 0.038] |
| **labelled not** | FP 0 | TN 190 | specificity 1.000 (190/190) [0.980, 1.000] |
|  | precision n/a (0/0) | NPV 0.660 (190/288) [0.603, 0.712] | accuracy 0.660 (190/288) [0.603, 0.712] |

prevalence 0.340 (98/288) [0.288, 0.397] · F1 0.000 (0/98) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · window · rule F6 (288 units)

|  | predicted F6 | predicted not |  |
|---|---|---|---|
| **labelled F6** | TP 0 | FN 31 | sensitivity 0.000 (0/31) [0.000, 0.110] |
| **labelled not** | FP 0 | TN 257 | specificity 1.000 (257/257) [0.985, 1.000] |
|  | precision n/a (0/0) | NPV 0.892 (257/288) [0.851, 0.923] | accuracy 0.892 (257/288) [0.851, 0.923] |

prevalence 0.108 (31/288) [0.077, 0.149] · F1 0.000 (0/31) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · window · rule F7 (288 units)

|  | predicted F7 | predicted not |  |
|---|---|---|---|
| **labelled F7** | TP 0 | FN 36 | sensitivity 0.000 (0/36) [0.000, 0.096] |
| **labelled not** | FP 0 | TN 252 | specificity 1.000 (252/252) [0.985, 1.000] |
|  | precision n/a (0/0) | NPV 0.875 (252/288) [0.832, 0.908] | accuracy 0.875 (252/288) [0.832, 0.908] |

prevalence 0.125 (36/288) [0.092, 0.168] · F1 0.000 (0/36) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · window · rule F8 (288 units)

|  | predicted F8 | predicted not |  |
|---|---|---|---|
| **labelled F8** | TP 0 | FN 39 | sensitivity 0.000 (0/39) [0.000, 0.090] |
| **labelled not** | FP 0 | TN 249 | specificity 1.000 (249/249) [0.985, 1.000] |
|  | precision n/a (0/0) | NPV 0.865 (249/288) [0.820, 0.899] | accuracy 0.865 (249/288) [0.820, 0.899] |

prevalence 0.135 (39/288) [0.101, 0.180] · F1 0.000 (0/39) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · window · rule F9 (288 units)

|  | predicted F9 | predicted not |  |
|---|---|---|---|
| **labelled F9** | TP 0 | FN 8 | sensitivity 0.000 (0/8) [0.000, 0.324] |
| **labelled not** | FP 0 | TN 280 | specificity 1.000 (280/280) [0.986, 1.000] |
|  | precision n/a (0/0) | NPV 0.972 (280/288) [0.946, 0.986] | accuracy 0.972 (280/288) [0.946, 0.986] |

prevalence 0.028 (8/288) [0.014, 0.054] · F1 0.000 (0/8) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

## Disagreements

Public units the predictor got wrong, false negatives first.

| tier | label | runs missed | text |
|---|---|---|---|
| gold | rewrite | 1 | Reads SAMPLE_CONFIG and does not change it |
| gold | rewrite | 1 | member order is the report's order of findings and of by_kind |
| gold | rewrite | 1 | Logs go to stderr as JSONL so that the report on stdout stays pipeable. |
| gold | cut | 1 | 'line 4' in a billing file, 'resources[3]' in a scan file |
| gold | cut | 1 | every billed_not_found has a cost |
| gold | cut | 1 | ASCII digits only: no sign, no space, no underscore, no other script's digits |
| gold | cut | 1 | int() alone also takes a sign, spaces, underscores and non-ASCII digits |
| gold | rewrite | 1 | databases written before account_id existed lack the column |
| gold | cut | 1 | bool is a subclass of int, and `true` in the rules file is a type error. |
| gold | cut | 1 | basename of an inventory file |
| gold | cut | 1 | ASCII digits only: no sign, space or underscore |
| gold | rewrite | 1 | `executemany` takes one sequence per row and rejects a dataclass with `ProgrammingError: parameters are of unsupported type`, so the row ... |
| gold | cut | 1 | line_num is the line on which the row just read ends |
| gold | cut | 1 | one hop, not transitive: with a -> b and b -> c, a resolves to b and c stays c |
| gold | cut | 1 | Amounts are in cents. |
| gold | rewrite | 1 | read-only: NEVER write inside the input directory, or a later run reads the output |
| gold | cut | 1 | a half-read rules file or a missing directory leaves nothing to reconcile, so neither the report nor the database is written |
| gold | cut | 1 | as typed, for the report's input_dir |
| gold | rewrite | 1 | signed, not absolute |
| gold | rewrite | 1 | in the order they were read |
| gold | rewrite | 1 | a name stands for itself and its one-hop alias: with a -> b and b -> c, a matches b but not c |
| gold | cut | 1 | billed_not_found always has monthly_cents |
| gold | cut | 1 | the bytes above the quota, and 0 when the team is within the quota |
| gold | cut | 1 | bool is an int subclass, so JSON true would pass the int check |
| gold | cut | 1 | A blank line is not a record. Without this, every file that ends in a newline would reject a phantom row. |
| gold | rewrite | 1 | Retry once: the endpoint drops the first request after an idle period. |
| gold | cut | 1 | returns the reason as a string when the row is rejected |
| gold | cut | 1 | returns the problem that rejects the entry, or None once the entry is accepted |
| gold | cut | 1 | None for a file of unknown format, which is never opened |
| gold | cut | 1 | bytes, not read_text(): universal newlines would rewrite a carriage return inside a CSV field |
| gold | rewrite | 1 | order matters: a repeated resource_id is accepted from the first file only |
| gold | rewrite | 1 | a library caller that configures no logging sees nothing, not the last-resort stderr handler |
| gold | cut | 1 | an operator can act on a per-file tally, and not on one rejected row of ten thousand |
| silver | cut | 1 | An entry is untrusted, so every field is checked here and nowhere downstream. |
| silver | rewrite | 1 | Load one file of any finance format into the billing side. Every finance format shares `seen`, so a resource billed in two finance files,... |
| silver | rewrite | 1 | NOT `-q`: quiet suppresses the very lines this counts, so a failing file scored zero. |
| silver | cut | 1 | Every request in this protocol is one line, so a write plus a drain is the whole of sending. |
| silver | cut | 1 | raises ValueError on junk |
| silver | rewrite | 1 | LBYL: the session is torn down before every reconnect, so no session here means a real bug. |
| silver | cut | 1 | The decorator is applied here rather than at module level, so that reading the file top-down never lands on a call to something defined f... |

181 more not shown.
