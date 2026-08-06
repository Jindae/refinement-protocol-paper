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
