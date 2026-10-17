# Coverage of the full skill in narrative-lite

Each row is a line of `skill/SKILL.md` or `skill/architecture.md` with a decision id on it, and the
location of the same rule in `skill-lite/`. `kept` means the rule is in lite, usually shorter and
without its id. `merged` and `moved` name the new location. A **cut** row is a rule or statement
that lite users do not get. The rows come from the id citations, and a statement with no id is not
listed here.

## Cut rules

These rows are cut entirely. The user approved every cut on 2026-10-15:

| line | ids | full skill | reason |
|---|---|---|---|
| `SKILL.md:174` | R2b-B2 | Collection literals get one item per line wherever ruff format explodes … | the bullet is a description of `ruff format` output, and tooling.md has it |
| `SKILL.md:320` | R4-03 | Speed does not change this. The difference between the forms is below ru… | speed evidence, below run-to-run noise |
| `architecture.md:143` | R7-B04 | Naming a concept and crossing a boundary are two tests, and they can dis… | unresolved, "no order between them is settled" |
| `architecture.md:144` | R8-D39 | Naming a concept and crossing a boundary are two tests, and they can dis… | with architecture.md:143 |
| `architecture.md:294` | R2-02, R7-C08 | The module doing the work collects per-item failures, and the module abo… | states that nothing changes at module scale |
| `architecture.md:317` | R7-indent, R7-indent-resolved | Take ruff format's signature indentation.  A hanging double | `ruff format` enforces the indentation |
| `architecture.md:325` | R7-A05-levels | Dependency direction. No layer table, no directory rule. | restated list. The rule is kept above it |
| `architecture.md:326` | R7-A05-property | Where a fact belongs. Ownership is a judgement about meaning. | restated list. The rule is kept above it |
| `architecture.md:327` | R7-B02, R7-B01-B03-criterion | The split axis, and whether a concern is coherent. | restated list. The rule is kept above it |
| `architecture.md:328` | R7-C05-naming | Whether a bundle is a real thing. | restated list. The rule is kept above it |

These cuts have no id, and are not in the table below:

- `architecture.md`: a second statement of the `Protocol` rule of `SKILL.md`
- **Show the thing**: the "avoid the same table as prose" counter-example and the size-conversion
  example
- **Comments**: about one example in three. Every kind, test and **Never** entry is kept
- **Verify**: the run-order and exit-code explanations, cut to one line each. The tool defaults
  that break rules are in `tooling.md`, unchanged

Five statements were dropped in the first draft and then restored, because each one is a rule:

- the slow stateful property test as opt-in
- for a module that computes records, paste the records
- a docstring sentence that is false of the code, or a consequence of an earlier sentence
- a flat log-field list as a smell once two producers need different keys
- clock injection only for a measured speedup

## Every cited line

| line | ids | full skill | lite |
|---|---|---|---|
| `SKILL.md:8` | R2b-P0 | 0% of reader effort on rote diffing, 100% on design.  Every rule below i… | kept: header |
| `SKILL.md:19` | R3-P2-rank | Second principle, for representation choices: prefer what the type check… | kept: header |
| `SKILL.md:74` | Q10 | main() returns an exit code. Call it as sys.exit(main()). All executable… | kept: File layout |
| `SKILL.md:78` | R2-10, R3a-03 | Caller before callee throughout. At module level, do not call or subclas… | kept: File layout |
| `SKILL.md:82` | R4-03 | That is an ordering rule, not a placement ban. A constant whose value is… | kept: File layout |
| `SKILL.md:86` | R3a-16, R3a-15 | Order constants by concern. Constants a dev would look for at the same m… | kept: File layout |
| `SKILL.md:92` | R3a-01 | Separate logically self-contained blocks inside a function with one blan… | kept: File layout |
| `SKILL.md:95` | R8-NAR008, R8-NAR008-rule | No tool checks this. | kept: File layout |
| `SKILL.md:108` | R4-05 | If a guard grows to three lines because it logs before raising, move the… | merged: SKILL.md › Errors, raise-site helper |
| `SKILL.md:112` | R2b-B1 | A def with >3 positional arguments puts each on a separate line with a t… | kept: File layout |
| `SKILL.md:117` | R5-06 | Keyword-only parameters do not count, so a function may take any number … | kept, File layout. Cut: the note that NAR004 counts every parameter (linter) |
| `SKILL.md:120` | Q03 | Long strings: implicit concatenation in parens. Never """ for data, beca… | kept: File layout |
| `SKILL.md:124` | R7-E07-floor | ruff targets py311. Check with vermin -t=3.11- --violations. | kept: Python 3.11 floor |
| `SKILL.md:128` | R7-E07-floor, R10-taskgroup-scope | Run tasks that should fail together in an asyncio.TaskGroup. Hand-rolled… | moved: domains.md › asyncio |
| `SKILL.md:131` | R3a-06 | except TimeoutError is correct around asyncio.wait_for. At 3.11 asyncio.… | moved: domains.md › asyncio |
| `SKILL.md:136` | R10-version-guard | On a guard for a runtime newer than the floor, the comment has the versi… | moved: domains.md › asyncio |
| `SKILL.md:140` | Q06 | Guard clauses and early return over nesting. | kept: Structure inside a function |
| `SKILL.md:144` | R10-positive-guard | Write a skip guard as the negation of what a valid item is. if not (name… | kept: Structure inside a function |
| `SKILL.md:147` | Q07 | Comprehensions may have any number of if clauses at a single level. Any … | kept: Structure inside a function |
| `SKILL.md:152` | R2-09, R2b-E1, R2b-E2 | Extract a block when you can foresee reusing or testing it separately, n… | kept: Structure inside a function |
| `SKILL.md:158` | R7-C05-resolved, R7-C05-naming | If an extracted function would take 5+ parameters, that is a missing own… | kept: Structure inside a function |
| `SKILL.md:161` | R2b-E4 | Always collapse duplicated-but-drifting code, even when the shared versi… | kept: Structure inside a function |
| `SKILL.md:164` | R2b-B4 | Mixed and/or parenthesises each group explicitly. Never A and B or C and… | kept: Structure inside a function |
| `SKILL.md:169` | R2b-B5 | Merge branches that share a body only where the type checker narrows the… | kept: Structure inside a function |
| `SKILL.md:174` | R2b-B2 | Collection literals get one item per line wherever ruff format explodes … | **cut**: the bullet is a description of `ruff format` output, and tooling.md has it |
| `SKILL.md:182` | Q11 | Spell names out. No img_arr, cfg, idx. | kept: Naming |
| `SKILL.md:187` | R9-03 | A function name starts with a verb, and the verb's object is what the fu… | kept: Naming |
| `SKILL.md:192` | R9-03, R7-B06 | A name is clear without its module, and the module qualifier does not co… | kept: Naming |
| `SKILL.md:197` | Q12 | Predicates are bare adjectives, and take no verb: readyForScan, not isRe… | kept: Naming |
| `SKILL.md:201` | Q11 | Do not restate a domain type in a parameter name: config: RebinConfig, n… | merged with the generic-type naming bullet |
| `SKILL.md:209` | R10-raw-names | Raw and parsed forms get different names. Prefix the raw form with raw_:… | kept: Naming |
| `SKILL.md:213` | R8-B06-Q11 | Restate the type where the bare name would shadow an import. A program t… | kept: Naming |
| `SKILL.md:217` | R3a-08 | from pathlib import Path, not pathlib.Path. Avoid fully qualified names,… | kept: Naming |
| `SKILL.md:221` | Q09 | Name every magic number.  Then place it by this test: | kept: Constant placement |
| `SKILL.md:229` | R3a-12 | The latter is an implementation detail and belongs inside the function, … | kept: Constant placement |
| `SKILL.md:236` | R2-11 | Annotate every parameter and return. mypy strict = true, disallow_any_ex… | kept: Types |
| `SKILL.md:239` | Q13 | Annotate the true requirement. A function that only iterates should use … | kept: Types |
| `SKILL.md:241` | Q15 | NewType for domain primitives (ScanId, SampleRef), so a bare int is a ty… | kept: Types |
| `SKILL.md:245` | R3a-10, R10-path-type | A file path is a Path from the boundary inward. A str path only where an… | kept: Types |
| `SKILL.md:253` | R10-money-cents, R10-money-decimal | Money is exact. Parse an amount with Decimal(raw) from the string, never… | moved: domains.md › Money |
| `SKILL.md:258` | R10-pendulum, R10-pendulum-boundary | Dates and times use pendulum, unless datetime is tightly integrated with… | moved: domains.md › Dates and times |
| `SKILL.md:260` | R2-08 | Enum for closed sets, .value at serialisation boundaries. Not Literal, n… | kept, Types › Enum bullet, merged with the IntEnum/StrEnum text |
| `SKILL.md:263` | R2-01 | Protocol for a seam with more than one real implementation. Never ABC, b… | kept: Types |
| `SKILL.md:267` | R8-D27-resolved | An annotation you cannot say out loud needs a name. The test is conversa… | kept: Types |
| `SKILL.md:271` | R8-D27 | The measure is how many names it contains, below the outermost. Car cont… | kept: Types |
| `SKILL.md:276` | R8-D27, R10-namedtuple-rows | The DB-API is the standing exception. sqlite3.executemany takes a sequen… | moved: domains.md › SQLite and the DB-API |
| `SKILL.md:293` | Q15 | The reason is a shared name, not type safety. Only NewType makes swapped… | kept. **Cut**: "only NewType makes swapped coordinates a type error" |
| `SKILL.md:311` | Q18, R3a-07 | A case _: raise RuntimeError(...) | kept: Types › Exhaustive dispatch |
| `SKILL.md:320` | R4-03 | Speed does not change this. The difference between the forms is below ru… | **cut**: speed evidence, below run-to-run noise |
| `SKILL.md:326` | R4-03, R7-E07-floor | IntEnum is not a substitute. It makes json.dumps({'level': LogLevel.INFO… | kept, Types › Enum bullet. Cut: the `str()` change across releases |
| `SKILL.md:332` | Q02, Q14, Q17 | Parse untrusted input into a frozen dataclass at one boundary gate, then… | kept: Data at boundaries |
| `SKILL.md:337` | R9-01 | A parsed record contains only what its input contained. Where one input … | kept: Data at boundaries |
| `SKILL.md:347` | R8-D10, R10-pydantic | Pydantic can be used for standardizing user input, at the boundary gate,… | kept: Data at boundaries |
| `SKILL.md:351` | R10-pydantic | No framework should validate output. FastAPI makes a route's return anno… | moved: domains.md › Web frameworks |
| `SKILL.md:355` | R8-D11-resolved | frozen=True is the default for every dataclass. It has nothing to do wit… | kept: Data at boundaries |
| `SKILL.md:366` | R4-04 | Genuinely schemaless input: promote the fields the program computes on t… | kept. Cut: the reasons against a JSON string (`json.loads` twice, `jq`) |
| `SKILL.md:384` | Q17, R6-03, R6-07 | An ORM is fine where it makes database work easier, as long as it adds n… | kept: Data at boundaries |
| `SKILL.md:385` | R7-D04, R7-D04-generalised, R10-orm-validation | An ORM is fine where it makes database work easier, as long as it adds n… | kept. Cut: the per-row and hot-path cost reason |
| `SKILL.md:389` | Q20 | Custom exception types subclassing RuntimeError, not Exception. | kept: Errors |
| `SKILL.md:394` | Q19 | Handle each failure mode narrowly and separately. Never one try around t… | kept: Errors |
| `SKILL.md:400` | R8-D24-resolved | Related means the handling is the same, not that the classes share a bas… | kept: Errors |
| `SKILL.md:402` | Q21 | raise NewError(...) from exc, and log it. Both. | kept: Errors |
| `SKILL.md:405` | R10-expected-form | An error message for malformed input includes the expected form. bad --n… | kept: Errors |
| `SKILL.md:410` | Q23, R4-02 | Log the generic fact once at the raise site, however you factor that. A … | kept: Errors |
| `SKILL.md:416` | R4-02 | At the handle site, log what the failure meant there, but in a degrade-a… | kept: Errors |
| `SKILL.md:420` | R4-02 | Level follows from what an operator can act on. A per-item failure is DE… | kept: Errors |
| `SKILL.md:423` | Q22 | LBYL over EAFP. You know your invariants, you do not know every exceptio… | kept: Errors |
| `SKILL.md:426` | Q24 | Degrade and report: process the whole batch, collect failures, log a sum… | kept: Errors |
| `SKILL.md:428` | R8-D25-resolved, Q24 | The config gate is the exception.  Q24 governs the batch a program | kept: Errors |
| `SKILL.md:436` | R2b-G1 | global marks a side effect, not a dependency. Declare it when a function… | kept: Module state |
| `SKILL.md:443` | V-03 | NAR001 also counts a call to a method whose name starts with a configura… | merged into the `global` bullet |
| `SKILL.md:445` | Q04 | Every attribute declared in __init__. hasattr(self, ...) is a red flag. | kept: Module state |
| `SKILL.md:450` | Q08 | One stable event name plus structured extra={...} fields, never an f-str… | kept: Logging |
| `SKILL.md:455` | R10-nullhandler | Get each module's logger with logging.getLogger(__name__). In a package … | moved: domains.md › Logging setup |
| `SKILL.md:457` | R5-03 | JSONL output is for machine reading. For terminal output, don't use JSON… | kept: Logging |
| `SKILL.md:458` | R8-D23-resolved | JSONL output is for machine reading. For terminal output, don't use JSON… | kept: Logging |
| `SKILL.md:469` | R5-09 | Do not use basicConfig(format='%(levelname)s %(message)s'). The standard… | kept. FieldFormatter code moved to domains.md › Logging setup |
| `SKILL.md:492` | R3a-02 | 1. A config file tracked in the repo, parsed into a frozen dataclass. Th… | kept: Configuration, concurrency |
| `SKILL.md:496` | R2-06 | 3. Environment for secrets and DB URLs, via python-decouple, not os.envi… | kept: Configuration, concurrency |
| `SKILL.md:502` | R2-04 | asyncio is the default for I/O-bound work. | kept: Configuration, concurrency |
| `SKILL.md:508` | R2-02, Q16 | Real dependencies: a real socket on loopback, a real temp SQLite file, a… | kept. Cut: "with a fake transport, tests pass while production fails" |
| `SKILL.md:512` | R2-12 | Property-based tests (hypothesis) wherever there is an invariant: round-… | kept: Testing |
| `SKILL.md:529` | R5-02 | Every module opens with a docstring. Anything runnable has a usage examp… | kept: The module docstring |
| `SKILL.md:535` | R9-09 | Write for a professional developer who has the file open. That reader kn… | kept: The module docstring |
| `SKILL.md:570` | R9-08 | Where a module reads or writes concrete text, paste a real sample of tha… | kept: Module docstring › Show the thing |
| `SKILL.md:631` | R9-09 | The summary line is mandatory. A body is not, and usually does not earn … | kept: Docstring rules |
| `SKILL.md:658` | R9-02 | Stop at the fact. The first malformed field stops the read. is the rule.… | kept: Docstring rules |
| `SKILL.md:676` | Q05, R2-03, R2-05, R5-05, R8-D18-resolved | A function gets a docstring when its contract is complex, meaning it tak… | kept, one line. Cut: "raising is not a trigger" and the fragmentation reason (NAR004) |
| `SKILL.md:684` | R8-D28-resolved | The docstring has a summary and a Raises: section. It has Args: and Retu… | kept: Docstring rules |
| `SKILL.md:696` | Q05 | Write nothing in a docstring that the code does not do, and no consequen… | kept, Docstring rules › cut list |
| `SKILL.md:702` | R9-02 | A docstring is about its file alone. Do not assert what another module d… | merged: Comments › Never › guarantees about other modules |
| `SKILL.md:705` | R3a-11 | Where semantics vary by implementation (file moves, copies, path manipul… | merged: Module docstring › Show the thing |
| `SKILL.md:709` | R10-Q25 | Test: what information is in this comment and not in the code? | kept: Comments |
| `SKILL.md:712` | R10-docstrings, R10-message-scope | These rules cover docstring prose, error messages and --help text too. v… | kept: Comments |
| `SKILL.md:716` | R10-stance | Comments are not thinking traces. While writing, you reasoned through ed… | kept: Comments |
| `SKILL.md:720` | R10-restatement-gate | Cut a comment whose content a smart reader would get from the code below… | kept: Comments |
| `SKILL.md:725` | R10-cleanup-rewrite | When shortening an existing comment, rewrite the sentence. Do not delete… | kept: Comments |
| `SKILL.md:727` | R10-topic-lists, R10-fp-fn, R10-kinds | Comment kinds: | kept: Comments |
| `SKILL.md:731` | R10-Q10, R10-Q14, R10-Q23, R10-Q34, R10-Q43, R10-Q48, R10-Q51, R10-business-case, R10-audience | Source: a fact or requirement from outside the code. Test: it would stil… | kept: Comments |
| `SKILL.md:741` | R10-Q20, R10-Q42, R10-Q44, R10-Q45, R10-Q50, R10-Q53, R10-Q55, R10-fence-consequence | Fence: code that looks unusual, where the obvious simplification silentl… | kept: Comments |
| `SKILL.md:749` | R10-Q42, R10-Q46 | Decoding aid: a line a smart reader would need docs or a worked example … | kept: Comments |
| `SKILL.md:755` | R10-regex-sample, R10-regex-literals | a regex gets a string it matches, and one it rejects where the boundary … | kept: Comments |
| `SKILL.md:764` | R10-candor, R10-Q03, R10-Q05, R10-Q36, R10-Q38, R6-12, R8-block-comments | Marker: no test needed. | kept: Comments |
| `SKILL.md:768` | R8-D02 | FIXME: incorrect behaviour, or behaviour that breaks soon after deploy. … | kept. Cut: the reachability details (NAR010) |
| `SKILL.md:771` | R10-block-label-size | a label on a block of at least 4 lines, ideally 6 or more: # parse data | kept: Comments |
| `SKILL.md:776` | R10-Q01, R10-Q06, R10-Q39, R10-Q47, R10-Q54 | what the next line or a single call does | kept: Comments |
| `SKILL.md:777` | R10-Q19, R10-Q21, R10-Q26, R10-Q49 | standard library or language behaviour the reader knows: <=, case sensit… | kept: Comments |
| `SKILL.md:778` | R9-02, R10-Q01 | why the file follows this style guide: so this is a class and not a modu… | kept: Comments |
| `SKILL.md:779` | Q08, R7-D04-comments | decision ids such as | kept: Comments |
| `SKILL.md:780` | R10-Q04, R10-Q08, R10-Q52 | changelog: an earlier state of the code, or a fixed bug with nothing lef… | kept: Comments |
| `SKILL.md:781` | R10-Q07, R10-rather-than | alternatives never in the code (rather than, instead of), except in arch… | kept: Comments |
| `SKILL.md:782` | R10-Q13, R10-rating | risks far outside the task's scale, and decisions too inconsequential fo… | kept: Comments |
| `SKILL.md:783` | R10-Q15 | future needs nobody has documented or planned | kept: Comments |
| `SKILL.md:784` | R10-candor, R10-Q20 | reassurance that a weakness is fine, such as deliberately or on purpose | kept: Comments |
| `SKILL.md:788` | R10-Q24, R10-Q11, R10-other-modules, R10-check-invariant | guarantees about other modules or functions. Put a module's guarantee in… | kept: Comments |
| `SKILL.md:791` | R10-usage-placement | how one function uses a type, written on the type: member order is the o… | kept. Cut: the plan.json example |
| `SKILL.md:792` | R10-Q21 | illustrations of a decision just discussed in the session | kept: Comments |
| `SKILL.md:793` | R10-return-contract | a function's return contract. State it in the docstring, and only if the… | kept: Comments |
| `SKILL.md:803` | R10-Q16, R10-seed-2, R10-depth-sentences | Depth: in proportion to the idea's difficulty for the reader. # signed e… | kept: Comments › Sentence form |
| `SKILL.md:804` | R10-depth-example, R10-period-join | Depth: in proportion to the idea's difficulty for the reader. # signed e… | kept: Comments › Sentence form |
| `SKILL.md:807` | R10-Q26, R10-Q35, R10-docstrings | a one-line # comment has a lowercase start and no final period. Several … | kept: Comments › Sentence form |
| `SKILL.md:810` | R10-period-join | two sentences over a connective such as which or since. With a connectiv… | kept: Comments › Sentence form |
| `SKILL.md:811` | R10-seed-10, R10-terse-narrow | terse. Drop articles where nothing is lost, never the subject or the ver… | kept: Comments › Sentence form |
| `SKILL.md:816` | R10-subject-verb | every clause has a subject and a verb. A label for the thing is fine: # … | kept: Comments › Sentence form |
| `SKILL.md:828` | R10-stand-in | a stand-in such as the one, it or that takes the place of a noun that fi… | kept: Comments › Sentence form |
| `SKILL.md:829` | R10-referent | a stand-in such as the one, it or that takes the place of a noun that fi… | kept: Comments › Sentence form |
| `SKILL.md:831` | R10-nominal-chain | the concrete thing, not what the X does to the Y: Say what the fact requ… | kept: Comments › Sentence form |
| `SKILL.md:842` | R10-case-coverage | in an error message, advise only steps the program has not taken: no pol… | kept: Comments › Sentence form |
| `SKILL.md:846` | R10-alternative-marker | when a comment moves from one approach to another, mark the switch with … | kept: Comments › Sentence form |
| `SKILL.md:847` | R10-seed-1, R10-seed-9, R10-Q32 | possessives and noun compounds over relative clauses: the archive's coll… | kept: Comments › Sentence form |
| `SKILL.md:848` | R10-seed-3, R10-seed-4 | trade terms over paraphrase: has no side effects. Modifiers before the n… | kept: Comments › Sentence form |
| `SKILL.md:852` | R10-conclusion | the conclusion, not the derivation. State what the code means, not how i… | kept: Comments › Sentence form |
| `SKILL.md:855` | R10-intensifiers | no intensifiers. Drop a word that only stresses, such as exactly, always… | kept: Comments › Sentence form |
| `SKILL.md:856` | R10-clipped-terms | the full term when a short form is ambiguous: timezone, not zone | kept: Comments › Sentence form |
| `SKILL.md:857` | R10-Q28, R10-Q29, R10-we | contractions and the imperative | kept: Comments › Sentence form |
| `SKILL.md:858` | R10-Q30, R10-Q35 | callables as name(), and no article before an identifier | kept: Comments › Sentence form |
| `SKILL.md:859` | R10-Q22, R10-Q21 | only names the reader can resolve from the comment's position | kept: Comments › Sentence form |
| `SKILL.md:864` | R10-Q31, R10-Q39, R10-seed-1, R10-seed-6, R10-seed-15, R10-skill-gaps | with code or an abstract noun as the subject, only verbs for what code l… | kept: Comments › Sentence form |
| `SKILL.md:865` | R10-Q40, R10-Q41 | no is what, no its own | kept: Comments › Sentence form |
| `SKILL.md:866` | R10-Q40 | the general case: records are separated by blank lines, not two records | kept: Comments › Sentence form |
| `SKILL.md:868` | R10-worked-example | a worked example matches what the code does for every case in it: not wi… | kept: Comments › Sentence form |
| `SKILL.md:869` | R10-no-semicolon | no semicolon and no dash. Write two sentences | kept: Comments › Sentence form |
| `SKILL.md:876` | R10-fence-form, R10-fence-fact, R10-fence-alternative | a Fence is the fact the code depends on, then the step the code takes be… | kept: Comments › Sentence form |
| `SKILL.md:884` | R10-branch-comment | a comment on one branch of a match or if chain is about what only that b… | kept: Comments › Sentence form |
| `SKILL.md:888` | R10-Q34, R10-locality, R10-fence-form, R10-argument-placement | directly above the statement it concerns, not above its enclosing block.… | kept: Comments › Sentence form |
| `SKILL.md:894` | R10-lint, R10-skill-gaps, R10-list-dash, R10-nar015-scope | NAR012 to NAR016 and NAR018 flag six wording faults in comments and docs… | one line: verify.py flags some faults. Cut: the NAR015 note about data |
| `SKILL.md:895` | R10-nar016, R10-nar018 | NAR012 to NAR016 and NAR018 flag six wording faults in comments and docs… | one line, with SKILL.md:894 |
| `SKILL.md:904` | R10-agentverb-check, R10-agentverb-agency | NAR017 is an agent verb on a subject that cannot act, meaning a noun tha… | merged into the agent-verb bullet |
| `SKILL.md:908` | R10-subject-verb, R10-nar020 | NAR020, from the same check, is a clause with no subject before , so: Na… | merged into the subject-and-verb bullet |
| `SKILL.md:914` | R10-procedures | Take these in order. Setup happens once per machine and once per project… | kept: Procedures |
| `SKILL.md:919` | R10-setup | Once per machine, make one lint venv and reuse it for every project. A v… | kept. Cut: the 430 MB note, `--venv`, the update mechanics |
| `SKILL.md:951` | R10-Q25, R10-Q27, R10-Q16 | 1. Rename first. If the information fits in a name or a type, rename and… | kept: Comments › Before writing |
| `SKILL.md:957` | R10-Q19, R10-footgun | 2. Guarantee it in code. Establish a cheap precondition, such as sorted … | kept: Comments › Before writing |
| `SKILL.md:958` | R10-hard-comment | 2. Guarantee it in code. Establish a cheap precondition, such as sorted … | kept: Comments › Before writing |
| `SKILL.md:963` | R10-keep-content | 3. Match a kind. Write a comment only if it is one of the four Comment k… | kept: Comments › Before writing |
| `SKILL.md:1002` | R10-prose-inventory, R10-closing-review | After a passing verify.py run, read the lists it prints, plus every erro… | kept, scoped to text written or changed in the task |
| `SKILL.md:1034` | R10-published-prose | Only the wording checks and agentverbs.py run on a page. Take the steps … | kept: Procedures › Published prose |
| `architecture.md:15` | R7-M01 | Name the change before you make it. The name must be enough for you to k… | kept: architecture.md › The measure |
| `architecture.md:24` | R7-A05-measure | Measure how much the person making an edit must know, not how many files… | kept: architecture.md › The measure |
| `architecture.md:30` | R7-M02 | The exchange rate, dearest first : | kept: architecture.md › The measure |
| `architecture.md:40` | R7-A05-property | Ask whose property the fact is, and put it in that thing's module. | kept: architecture.md › Fact placement |
| `architecture.md:48` | R7-A01-revised | Do not make a caller pass what the callee can compute from its arguments… | kept: architecture.md › Fact placement |
| `architecture.md:52` | R7-A04-revised | An exception type belongs in the shared vocabulary, not in the module th… | kept: architecture.md › Fact placement |
| `architecture.md:55` | R7-B07, R7-B07-bound | A type centralises once it appears in a signature.  A shape built and | kept: architecture.md › Fact placement |
| `architecture.md:60` | R8-D19-resolved | Every type in a signature that other modules use goes in the shared voca… | kept: architecture.md › Fact placement |
| `architecture.md:68` | R7-E02-fields | A log field set belongs to whatever emits the record, not to the formatt… | kept: architecture.md › Fact placement |
| `architecture.md:71` | R9-12 | A one-line body earns its name when the expression encodes a domain deci… | kept: architecture.md › Fact placement |
| `architecture.md:97` | R7-A05 | Two participants that must agree on a byte layout share one module, besi… | kept: architecture.md › Fact placement |
| `architecture.md:104` | R7-A05-levels | There is no layer table and no directory rule. This is review judgement,… | kept: architecture.md › Which module imports which |
| `architecture.md:110` | R7-A02 | A cycle is a wrong cut, not an import problem.  Break it with a shared v… | kept: architecture.md › Which module imports which |
| `architecture.md:116` | R7-B06, R3a-08 | Call a first-party module by name. from collector import store, then sto… | moved: SKILL.md › Naming |
| `architecture.md:122` | R9-03, R8-B06-Q11 | The qualifier is not part of the function name. store.insertReading read… | moved: SKILL.md › Naming |
| `architecture.md:128` | R7-B01-B03-criterion | A coherent concern earns a module. Line count is not the criterion, in e… | kept: architecture.md › Where the cuts go |
| `architecture.md:130` | R8-D12-resolved | The test is whether you can name it without saying "and".  retention.py … | kept: architecture.md › Where the cuts go |
| `architecture.md:132` | R7-C05-naming | and checksums", so the checksum leaves and gets a separate module. This … | kept: SKILL.md › Structure (missing owner) |
| `architecture.md:135` | R7-B01 | Split.  Six modules of 40 to 90 lines are better than one file of 340, b… | kept: architecture.md › Where the cuts go |
| `architecture.md:139` | R7-B02 | There is no fixed split axis.  Cut by technical role when the program ha… | kept: architecture.md › Where the cuts go |
| `architecture.md:143` | R7-B04 | Naming a concept and crossing a boundary are two tests, and they can dis… | **cut**: unresolved, "no order between them is settled" |
| `architecture.md:144` | R8-D39 | Naming a concept and crossing a boundary are two tests, and they can dis… | **cut**, with architecture.md:143 |
| `architecture.md:151` | R7-A05-growth | Shared code inside one system starts as one common.py, scoped to that sy… | kept: architecture.md › Where the cuts go |
| `architecture.md:157` | R7-B08, R7-B08-scope | Prefix every internal module-level name with an underscore: functions, c… | kept: architecture.md › Package surface |
| `architecture.md:164` | R7-B05 | __all__ declares a package's exports.  A library's __init__.py is a re-e… | kept: architecture.md › Package surface |
| `architecture.md:167` | R7-B09 | main is in __main__.py.  Users type python3 -m collector and never see t… | kept: architecture.md › Package surface |
| `architecture.md:170` | R7-A05-entry | The entry point has the list of modules and nothing about any of them.  … | kept: architecture.md › Package surface |
| `architecture.md:173` | R7-B01-map | The reading order is in __main__.py.  Its docstring is the program's pur… | kept. Cut: the stack-trace cost note |
| `architecture.md:180` | R9-02 | This is the one docstring with other modules' names in it, and the only … | kept: architecture.md › Package surface |
| `architecture.md:182` | R7-E05 | main()-first generalises to a library.  The public entry takes main()'s | kept. Cut: "it does not replace the module docstring" |
| `architecture.md:188` | R7-C01-C02-revised | Values that could differ between instances earn a class.  Two | kept: architecture.md › What earns a class, a Protocol, a bundle |
| `architecture.md:189` | R7-C02 | Values that could differ between instances earn a class.  Two | kept: architecture.md › What earns a class, a Protocol, a bundle |
| `architecture.md:197` | R7-C03 | One coordinator, not a chain.  Stages that nothing reuses separately do … | kept: architecture.md › What earns a class, a Protocol, a bundle |
| `architecture.md:200` | R7-C06, R7-C07 | A pure core earns its place by the number of decisions in it.  Four rout… | kept: architecture.md › What earns a class, a Protocol, a bundle |
| `architecture.md:204` | R7-A06 | Every case of a closed set is in one module, in an exhaustive match.  A … | kept: architecture.md › What earns a class, a Protocol, a bundle |
| `architecture.md:209` | R7-B07-preemption | Centralise a type before anything shares it. Do not generalise behaviour… | kept: architecture.md › What earns a class, a Protocol, a bundle |
| `architecture.md:215` | R7-A03 | A resource is opened at the scope whose lifetime it matches, and the rea… | kept: architecture.md › Resources, state and config |
| `architecture.md:217` | R7-A03-idle | Idle time is not the variable. What the handle costs on the far side is.… | kept: architecture.md › Resources, state and config |
| `architecture.md:221` | R7-E01 | A module-level singleton is fine for anything never closed.  A logger is… | merged with the config singleton paragraph |
| `architecture.md:225` | R7-E03 | One program-scoped config object reaches every module.  Per-module slice… | merged with the config singleton paragraph |
| `architecture.md:229` | R8-D09-resolved | The config object is a module-level singleton, not a parameter.  Parse t… | kept: architecture.md › Resources, state and config |
| `architecture.md:237` | R7-A07 | Leaf modules import the constants they need, when those constants exist … | kept: architecture.md › Resources, state and config |
| `architecture.md:240` | R7-C04 | Pass a flag no further down than the function that branches on it.  A fl… | kept: architecture.md › Resources, state and config |
| `architecture.md:243` | R7-E04 | The clock goes inside the function that reads it.  Test through the real… | kept: architecture.md › Resources, state and config |
| `architecture.md:251` | R7-D02 | Take the dependency when it is simpler at the call site.  The dependency… | kept: architecture.md › Third-party code |
| `architecture.md:254` | R7-D02-stdlib | Take the dependency when it is simpler at the call site.  The dependency… | kept: architecture.md › Third-party code |
| `architecture.md:256` | R7-D03, R7-D01 | Then contain it.  One module imports the library. Everything downstream … | kept: architecture.md › Third-party code |
| `architecture.md:259` | R7-D01-D03-containment | Contain handles, not values.  A handle is a thing that must be | kept: architecture.md › Third-party code |
| `architecture.md:260` | R7-D01-D03-handle | Contain handles, not values.  A handle is a thing that must be | kept: architecture.md › Third-party code |
| `architecture.md:265` | R7-D05, R7-D05-trust | Depend rather than vendor or reimplement, weighted by adoption: download… | kept. Cut: "a package can be popular and bad" |
| `architecture.md:269` | R7-D06 | A pin is a property of the deployment, never of the library.  A library … | kept: architecture.md › Third-party code |
| `architecture.md:275` | R7-E02 | One shared logger from one logs module.  A shared logger makes record.na… | kept: architecture.md › Service, library, monorepo |
| `architecture.md:277` | R7-E02-fields | One shared logger from one logs module.  A shared logger makes record.na… | kept: architecture.md › Service, library, monorepo |
| `architecture.md:279` | R7-E06 | Shared code goes in the shared library, not in whichever program used it… | kept: architecture.md › Service, library, monorepo |
| `architecture.md:281` | R7-E07 | The source pushes and the service follows, when the source supports it. … | kept: architecture.md › Service, library, monorepo |
| `architecture.md:287` | Q24 | Without rounds there is no natural batch, so the reporting unit becomes … | kept: architecture.md › Service, library, monorepo |
| `architecture.md:293` | Q24, R7-A08 | The module doing the work collects per-item failures, and the module abo… | kept: architecture.md › Where degrade-and-report splits |
| `architecture.md:294` | R2-02, R7-C08 | The module doing the work collects per-item failures, and the module abo… | **cut**: states that nothing changes at module scale |
| `architecture.md:307` | R7-return-naming | Name the value of the last return.  At the end of a long function, the n… | moved: SKILL.md › Structure |
| `architecture.md:310` | R2b-P0 | Name the value of the last return.  At the end of a long function, the n… | moved: SKILL.md › Structure, with architecture.md:307 |
| `architecture.md:313` | R7-A05-ordering | Order module constants by who changes the value.  Operator-tunable first… | moved: SKILL.md › File layout |
| `architecture.md:315` | R4-03 | Order module constants by who changes the value.  Operator-tunable first… | moved: SKILL.md › File layout |
| `architecture.md:317` | R7-indent, R7-indent-resolved | Take ruff format's signature indentation.  A hanging double | **cut**: `ruff format` enforces the indentation |
| `architecture.md:325` | R7-A05-levels | Dependency direction. No layer table, no directory rule. | **cut**: restated list. The rule is kept above it |
| `architecture.md:326` | R7-A05-property | Where a fact belongs. Ownership is a judgement about meaning. | **cut**: restated list. The rule is kept above it |
| `architecture.md:327` | R7-B02, R7-B01-B03-criterion | The split axis, and whether a concern is coherent. | **cut**: restated list. The rule is kept above it |
| `architecture.md:328` | R7-C05-naming | Whether a bundle is a real thing. | **cut**: restated list. The rule is kept above it |
