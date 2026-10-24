# Unit eval

**Run** deterministic, skill `core/tools` at 6ec9cf5 with uncommitted changes, content 2003853c4074, model none

- split dev, 1 run(s), started 2026-10-24 13:57, cost none
- 233 units, 233 predictions, 0 unanswered, 0 confidential units counted, 0 confidential units skipped

Human ceiling: no blind re-label yet. Run `eval/label.py --audit`.

## gold

### gold · none · overall (11 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 3 | FN 8 | sensitivity 0.273 (3/11) [0.097, 0.566] |
| **labelled not** | FP 0 | TN 0 | specificity n/a (0/0) |
|  | precision 1.000 (3/3) [0.439, 1.000] | NPV 0.000 (0/8) [0.000, 0.324] | accuracy 0.273 (3/11) [0.097, 0.566] |

prevalence 1.000 (11/11) [0.741, 1.000] · F1 0.429 (6/14) [0.000, 0.706] · balanced accuracy n/a · MCC n/a

### gold · none · language python (11 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 3 | FN 8 | sensitivity 0.273 (3/11) [0.097, 0.566] |
| **labelled not** | FP 0 | TN 0 | specificity n/a (0/0) |
|  | precision 1.000 (3/3) [0.439, 1.000] | NPV 0.000 (0/8) [0.000, 0.324] | accuracy 0.273 (3/11) [0.097, 0.566] |

prevalence 1.000 (11/11) [0.741, 1.000] · F1 0.429 (6/14) [0.000, 0.706] · balanced accuracy n/a · MCC n/a

### gold · none · rule NAR017 (171 units)

|  | predicted NAR017 | predicted not |  |
|---|---|---|---|
| **labelled NAR017** | TP 16 | FN 1 | sensitivity 0.941 (16/17) [0.730, 0.990] |
| **labelled not** | FP 0 | TN 154 | specificity 1.000 (154/154) [0.976, 1.000] |
|  | precision 1.000 (16/16) [0.806, 1.000] | NPV 0.994 (154/155) [0.964, 0.999] | accuracy 0.994 (170/171) [0.968, 0.999] |

prevalence 0.099 (17/171) [0.063, 0.153] · F1 0.970 (32/33) [0.889, 1.000] · balanced accuracy 0.971 [0.900, 1.000] · MCC 0.967 [0.883, 1.000]

### gold · snippet · overall (51 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 14 | FN 20 | sensitivity 0.412 (14/34) [0.264, 0.578] |
| **labelled not** | FP 4 | TN 13 | specificity 0.765 (13/17) [0.527, 0.904] |
|  | precision 0.778 (14/18) [0.548, 0.910] | NPV 0.394 (13/33) [0.247, 0.563] | accuracy 0.529 (27/51) [0.395, 0.659] |

prevalence 0.667 (34/51) [0.530, 0.780] · F1 0.538 (28/52) [0.364, 0.691] · balanced accuracy 0.588 [0.445, 0.712] · MCC 0.174 [-0.105, 0.409]

### gold · snippet · language python (51 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 14 | FN 20 | sensitivity 0.412 (14/34) [0.264, 0.578] |
| **labelled not** | FP 4 | TN 13 | specificity 0.765 (13/17) [0.527, 0.904] |
|  | precision 0.778 (14/18) [0.548, 0.910] | NPV 0.394 (13/33) [0.247, 0.563] | accuracy 0.529 (27/51) [0.395, 0.659] |

prevalence 0.667 (34/51) [0.530, 0.780] · F1 0.538 (28/52) [0.368, 0.689] · balanced accuracy 0.588 [0.453, 0.721] · MCC 0.174 [-0.087, 0.427]

## silver

### silver · snippet · overall (6 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 1 | FN 0 | sensitivity 1.000 (1/1) [0.207, 1.000] |
| **labelled not** | FP 2 | TN 3 | specificity 0.600 (3/5) [0.231, 0.882] |
|  | precision 0.333 (1/3) [0.061, 0.792] | NPV 1.000 (3/3) [0.439, 1.000] | accuracy 0.667 (4/6) [0.300, 0.903] |

prevalence 0.167 (1/6) [0.030, 0.564] · F1 0.500 (2/4) [0.000, 1.000] · balanced accuracy 0.800 [0.600, 1.000] · MCC 0.447 [0.200, 1.000]

### silver · snippet · language python (6 units)

|  | predicted fail | predicted not |  |
|---|---|---|---|
| **labelled fail** | TP 1 | FN 0 | sensitivity 1.000 (1/1) [0.207, 1.000] |
| **labelled not** | FP 2 | TN 3 | specificity 0.600 (3/5) [0.231, 0.882] |
|  | precision 0.333 (1/3) [0.061, 0.792] | NPV 1.000 (3/3) [0.439, 1.000] | accuracy 0.667 (4/6) [0.300, 0.903] |

prevalence 0.167 (1/6) [0.030, 0.564] · F1 0.500 (2/4) [0.000, 1.000] · balanced accuracy 0.800 [0.500, 1.000] · MCC 0.447 [0.200, 1.000]

### silver · snippet · rule F1 (6 units)

|  | predicted F1 | predicted not |  |
|---|---|---|---|
| **labelled F1** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 6 | specificity 1.000 (6/6) [0.610, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (6/6) [0.610, 1.000] | accuracy 1.000 (6/6) [0.610, 1.000] |

prevalence 0.000 (0/6) [0.000, 0.390] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

### silver · snippet · rule F2a (6 units)

|  | predicted F2a | predicted not |  |
|---|---|---|---|
| **labelled F2a** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 6 | specificity 1.000 (6/6) [0.610, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (6/6) [0.610, 1.000] | accuracy 1.000 (6/6) [0.610, 1.000] |

prevalence 0.000 (0/6) [0.000, 0.390] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

### silver · snippet · rule F2b (6 units)

|  | predicted F2b | predicted not |  |
|---|---|---|---|
| **labelled F2b** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 6 | specificity 1.000 (6/6) [0.610, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (6/6) [0.610, 1.000] | accuracy 1.000 (6/6) [0.610, 1.000] |

prevalence 0.000 (0/6) [0.000, 0.390] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

### silver · snippet · rule F3 (6 units)

|  | predicted F3 | predicted not |  |
|---|---|---|---|
| **labelled F3** | TP 0 | FN 1 | sensitivity 0.000 (0/1) [0.000, 0.793] |
| **labelled not** | FP 0 | TN 5 | specificity 1.000 (5/5) [0.566, 1.000] |
|  | precision n/a (0/0) | NPV 0.833 (5/6) [0.436, 0.970] | accuracy 0.833 (5/6) [0.436, 0.970] |

prevalence 0.167 (1/6) [0.030, 0.564] · F1 0.000 (0/1) [0.000, 0.000] · balanced accuracy 0.500 [0.500, 0.500] · MCC n/a

### silver · snippet · rule F4 (6 units)

|  | predicted F4 | predicted not |  |
|---|---|---|---|
| **labelled F4** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 6 | specificity 1.000 (6/6) [0.610, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (6/6) [0.610, 1.000] | accuracy 1.000 (6/6) [0.610, 1.000] |

prevalence 0.000 (0/6) [0.000, 0.390] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

### silver · snippet · rule F5 (6 units)

|  | predicted F5 | predicted not |  |
|---|---|---|---|
| **labelled F5** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 6 | specificity 1.000 (6/6) [0.610, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (6/6) [0.610, 1.000] | accuracy 1.000 (6/6) [0.610, 1.000] |

prevalence 0.000 (0/6) [0.000, 0.390] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

### silver · snippet · rule F6 (6 units)

|  | predicted F6 | predicted not |  |
|---|---|---|---|
| **labelled F6** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 6 | specificity 1.000 (6/6) [0.610, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (6/6) [0.610, 1.000] | accuracy 1.000 (6/6) [0.610, 1.000] |

prevalence 0.000 (0/6) [0.000, 0.390] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

### silver · snippet · rule F7 (6 units)

|  | predicted F7 | predicted not |  |
|---|---|---|---|
| **labelled F7** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 6 | specificity 1.000 (6/6) [0.610, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (6/6) [0.610, 1.000] | accuracy 1.000 (6/6) [0.610, 1.000] |

prevalence 0.000 (0/6) [0.000, 0.390] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

### silver · snippet · rule F8 (6 units)

|  | predicted F8 | predicted not |  |
|---|---|---|---|
| **labelled F8** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 6 | specificity 1.000 (6/6) [0.610, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (6/6) [0.610, 1.000] | accuracy 1.000 (6/6) [0.610, 1.000] |

prevalence 0.000 (0/6) [0.000, 0.390] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

### silver · snippet · rule F9 (6 units)

|  | predicted F9 | predicted not |  |
|---|---|---|---|
| **labelled F9** | TP 0 | FN 0 | sensitivity n/a (0/0) |
| **labelled not** | FP 0 | TN 6 | specificity 1.000 (6/6) [0.610, 1.000] |
|  | precision n/a (0/0) | NPV 1.000 (6/6) [0.610, 1.000] | accuracy 1.000 (6/6) [0.610, 1.000] |

prevalence 0.000 (0/6) [0.000, 0.390] · F1 n/a (0/0) · balanced accuracy n/a · MCC n/a

## Disagreements

Public units the predictor got wrong, false negatives first.

| tier | label | runs missed | text |
|---|---|---|---|
| gold | rewrite | 1 | Reads SAMPLE_CONFIG and does not change it |
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
| gold | cut | 1 | None for a file of unknown format, which is never opened |
| gold | cut | 1 | bytes, not read_text(): universal newlines would rewrite a carriage return inside a CSV field |
| gold | rewrite | 1 | order matters: a repeated resource_id is accepted from the first file only |
| gold | rewrite | 1 | a library caller that configures no logging sees nothing, not the last-resort stderr handler |
| gold | keep | 1 | bytes, then decode: read_text() translates \r\n, which the csv module must see untranslated |
| gold | keep | 1 | a str: Path() would drop a trailing slash that the report must echo |
| gold | keep | 1 | a digest and not a UNIQUE over the columns: SQLite treats every NULL as distinct in a UNIQUE key |
| gold | keep | 1 | per-record rejections log at DEBUG, so --verbose shows each one |
