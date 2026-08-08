# Paper Writing Guidelines

## Writing Style

* Do not use overly fancy words or overselling sentences.
* Use conservative, reviewer-safe arguments and claims.
* Be concise while providing sufficient details about the study.
* Do not start a paragraph with `Together, ...`, `Taken together, ...`, or similar expressions.
* When summarizing or combining previous paragraphs, use a more formal expression.

## Scope of the Paper

* Focus on what we actually did in the study.
* Describe only the final results and processes selected for inclusion in the paper.
* Do not describe rejected or dismissed ideas, hypotheses, processes, or results merely because they appear in project documents.
* Mention rejected or dismissed material only when it is necessary to justify and support a final decision included in the paper.

## Terminology

* Maintain consistent terminology for concepts related to the study.
* Do not use ambiguous or informal terms that were used only during implementation or experimentation.
* Use terms that clearly and precisely describe the relevant concept, process, or result.
* Refer to the project's Glossary document when selecting terminology.

## Positioning Decision-Conditioned Refinement

* Do not claim that this study first proposes selective refinement, refine-or-stop behavior, or the separation of a refinement decision from revision.
* Use ART as the closest precedent for a physically separate pre-refinement gate: a trained Asker conditionally invokes Refine, but also passes subquestions to it and is followed by a Truster.
* Use DeCRIM as an instruction-following precedent in which a separate Critic suppresses unnecessary refinement, while noting that its natural-language feedback is also the Refiner's input.
* Use Self-Refine as an earlier general framework whose Feedback call may emit a task-specific stop indicator, but do not describe it as a standalone binary Decision because feedback and critique are combined.
* Use GLoRe as construct-level evidence for separating when, where, and how. State that its main evaluation generates refinements before using an ORM to rerank them, so it is not evidence for pre-refinement call gating or token savings.
* Use ReVISE as the closest conventional code-generation precedent because it evaluates a learned `[eos]`/`[refine]` mechanism on MBPP. Describe it as a two-stage SFT+DPO curriculum for verification and correction, and distinguish its integrated next-token boundary from this study's standalone Decision call.
* Describe RubricRefine as adjacent code-mode tool-use evidence, not as conventional natural-language-to-function code generation.
* State the contribution as a controlled analysis of the separated Decision stage: its prevented regressions, missed repairs, exact preservation, and token savings under a shared-initial design and multiple refinement paths.
* Do not attribute ART, GLoRe, DeCRIM, Self-Refine, or ReVISE's complete-system performance gain solely to their decision or stopping component unless the cited experiment isolates that component.

## Positioning Revision Planning

* Use Self-Planning Code Generation as the primary direct precedent for separating a code-generation Planning phase from an Implementation phase. State that it supports the value of an explicit plan artifact before code realization, not the superiority of a separate post-critique call.
* Report the relevant Self-Planning variant result conservatively: its two-phase method outperformed Direct and Code CoT, but its one-phase plan-plus-code variant was slightly higher than the two-phase variant on the reported HumanEval comparison. The prompt information requirements also differed, so do not treat this as an isolated causal estimate of call separation.
* Use Planning-Driven Programming (LPW) as the closest code-specific bridge between planning and refinement. Explain that LPW generates and verifies a solution plan before initial code, reuses plan verification during debugging, and combines post-hoc error analysis with refinement suggestions. Its ablations concern plan verification or phase bundles, not a standalone post-critique Planning call.
* Describe the current Revision Planning stage as a variant of the general Critique-refinement pipeline: Critique diagnoses problem existence, root cause, and location; Planning translates that stored diagnosis into minimal change instructions and preservation constraints; CPR Revision receives only the plan.
* Treat CRAFT as auxiliary non-code evidence for plan-conditioned text revision. Explicitly state that its plan-generation prompt combines issue diagnosis and improvement strategy, making it less directly aligned with the study's independent Critique and Planning calls.
* Treat MapCoder, Chain-of-Verification, CritiCS, Plan-and-Solve, Structured CoT, and similar methods as structural or mechanism-level examples. Do not present them as direct evidence for the effect of post-critique Revision Planning in code self-refinement.
* Use generic Chain-of-Thought only as broad motivation for intermediate reasoning. Prefer Self-Planning and LPW for the direct argument because CoT commonly mixes diagnosis, planning, and execution and often remains within one response.
* Do not claim that this study first introduces planning to code generation, separates planning from implementation, or uses a revision plan as an intermediate artifact. State the narrower gap: prior work provides limited controlled evidence for inserting an independently observable Revision Planning call after a separately generated Critique and comparing the resulting `CPR` path with `CR` under shared initials and no execution feedback.
* Interpret `CPR - CR` as the effect of the complete protocol change: adding the Planning artifact and call and replacing Critique with Plan as the direct Revision input. Do not label it as the isolated causal effect of plan quality or call separation.

## Positioning Single-Call versus Multi-Call Protocols

* Describe RQ4 as a comparison of prompt-and-call topology, not as proof that an unobserved model reasoning trace followed C, P, D, or R internally.
* Compare `CR` with `SC-CR`, `CPR` with `SC-CPR`, and the three separate Decision-conditioned paths with their corresponding `SC-D*` paths using the same exact initial candidates.
* State that the main `SC-D*` outcome evaluates the code emitted in the same response regardless of its reported Decision label. Report label-enforced selection only as a supplementary derived outcome.
* Report `PRESERVE` with changed code and `REFINE` with unchanged code explicitly. Use these cases to discuss the exact-selection boundary of the separate Decision, not to claim that the integrated Decision is semantically dishonest.
* Use Self-Planning's one-phase and two-phase variants only as motivation that call realization can matter. Do not treat their result as an expected effect size because their task information and protocol differ.
* Keep RQ4 token accounting separate from RQ3 correctness and preservation. Single-call protocols naturally avoid intermediate artifact tokens, but lower token consumption alone does not establish a better refinement protocol.

### Discussing the Plan Result

* If `CPR` outperforms `CR`, describe this as evidence that explicit post-critique planning can improve the complete refinement path under the evaluated conditions. Compare it cautiously with the pre-generation planning gains in Self-Planning and the verified-plan workflow in LPW.
* If `CPR` matches or underperforms `CR`, discuss it alongside Self-Planning's slightly stronger one-phase variant. Consider information loss between Critique and Plan, propagated diagnosis errors, plan-following failures, extra context transformation, and model/task heterogeneity before drawing a conclusion.
* In either direction, decompose the difference into Repair, Correct-to-Incorrect Regression, Functional Preservation, and Unrepaired Failure. A similar final pass rate can conceal a different repair-regression balance.
* Report the Planning call and changed Revision-input token costs. Evaluate whether any correctness gain is Pareto-efficient or yields a reasonable token cost per additional correct solution.
* Keep LPW's visible-test and execution-trace supervision explicit when comparing results. Do not use its performance gain as an expected effect size for this execution-feedback-free study.
* Use artifact-level examples only to explain observed mechanisms, such as faithful Critique-to-Plan translation or failure to preserve unaffected behavior. Do not substitute qualitative examples for the predeclared paired protocol analysis.

## LaTeX Formatting

* Do not use `--` as punctuation. Use `-` only where a hyphen is grammatically required.
* In LaTeX source, place each sentence on a separate line. Do not insert a line break in the middle of a sentence or at an arbitrary point within a paragraph.

## Discussing Tables and Figures

When a Results section presents and discusses a table or figure, use the following paragraph structure.

### 1. Introduce the Table or Figure

* Briefly explain what the table or figure presents.
* Explain what the columns, rows, axes, or data points represent.

### 2. Discuss the Main Results

* Begin with the general, common, or central pattern shown by the data.

### 3. Discuss Specific Findings

* Continue with more specific or interesting findings observed in the data.
