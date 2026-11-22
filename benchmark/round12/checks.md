# Checks for the rules of round 12

Each check was measured before it got a code. The measures are the hits on the units of the rule in the batch, on the
13 rewrites of the user in the Claudish inbox, and on human comments: 1,289 GTNH comments at the last commit before 2023,
and 2,926 Python 3.10 comments. A hit on a human comment is not a false positive by itself, because human comments break
the rules too.

| rule | code | form | rule units | user rewrites | human GTNH | Python 3.10 |
|---|---|---|---|---|---|---|
| 1: negate the verb | `NAR025` | finding | 12 of 13 | 1 of 13 | 2.3% | 5.2% |
| 6: a condition is a clause | `NAR026` | finding | 6 of 6 | 0 of 13 | 0.6% | 0.6% |
| 7: no `X, not Y` | `NAR024` | finding | 16 of 16 | 0 of 13 | 0.5% | 0.4% |
| 10: no constant values | `NAR027` | finding | 0 of 2 | | | 1 hit in 585 files |
| 11: javadoc by the review list | `NAR116` | review list | | | | |
| 13: no free modifier | | review list | 6 of 7 | 0 of 13 | 1.3% | 2.0% |
| 15: no docstring on a function of one line | `NAR023` | finding | | | | |
| 2: no changelog | | no check | 13 of 21 | 2 of 13 | 4.4% | 7.7% |

- **Rule 1.** In a sample of 20 hits on human comments, about 15 have the form of the rule, such as `serve no specific
  purpose` and `there's nothing more to do`. The rest are the Python value `None`, which `NAR025` now leaves out, and
  labels without a verb.
- **Rule 6.** `NAR026` leaves out an opener with `for`. Most openers with `for` in the human comments are a purpose,
  such as `For back compatibility,`. An opener with a platform, such as `On Windows,`, is left out too.
- **Rule 10.** `NAR027` flags a number in a comment when the number is the value of a constant that the comment names, or
  of a constant on the 3 lines below the comment. The 2 rule units are config comment strings with the constants in
  another class, so `NAR027` doesn't reach them.
- **Rule 13.** The fourth review list of `verify.py` has each sentence with a free modifier. `, such as X` is left out,
  because you asked for more research on the form.
- **Rule 15.** `NAR023` leaves out a stub: a body of `...`, `pass` or `raise NotImplementedError`, and a function under
  `@abstractmethod` or `@overload`. Python `NAR004` skips a function of one line, so the two checks don't conflict.
- **Rule 2.** No check. A detector of the past tense had hits on 2 of your 13 rewrites, such as the participle
  `scanned`. A detector of `once` alone had hits on 3 of the 21 rule units, and on human uses such as `more than once`.

## The skill's own text

In the tools of the repository, the new checks have about 120 findings in text that was there before round 12, such as
`With --since REF,` (`NAR026`) and `The list is no finding` (`NAR025`). 9 functions of the tools have a docstring on a
body of one line (`NAR023`). These findings are for the de-poisoning pass, with the conflicts in `depoison_list.md`.

## Open

- Python `NAR004` is still a finding for a function with more than 3 parameters and no docstring. Rule 11 changed `NAR116` for Java
  only.
