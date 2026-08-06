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

## LaTeX Formatting

* Do not use `--` as punctuation. Use `-` only where a hyphen is grammatically required.
* In LaTeX source, place each sentence on a separate line. Do not insert a line break in the middle of a sentence or at an arbitrary point within a paragraph.

## Writing the Methodology Section

* Open the section with two or three sentences that state the controlled study design and the scope of the section.
* Organize the main account around Research Questions, Self-Refinement Protocols, Models and Benchmarks, and Experimental Setting. Adjust these subsections only when doing so makes a substantive methodological distinction clearer.
* Avoid fragmenting the section into many narrow subsections. Use short descriptive paragraphs or structured lists within the main subsections when details need separation.
* For each Research Question, first explain why the question matters, then identify at a high level the experiment or comparison used to answer it. Leave detailed metrics and procedures to the later methodological account.
* Describe each protocol stage as an observable prompt and model call, and distinguish a stage from its artifact and from a derived protocol outcome.
* Present the selected models and benchmarks in separate concise tables. Follow each table with the selection rationale, the intended coverage or comparison role, and any adopted exception that changes the final experimental scope.
* In Experimental Setting, report the procedure that was actually executed, including phase-wise execution and artifact reuse when protocols were not run independently end to end.
* Provide the hardware, software, inference parameters, evaluation environment, timeout policy, output contracts, and exception-handling rules needed to understand and reproduce the study.
* State the core methodological decision and its reason before adding implementation values or edge-case details.
* Include enough detail to explain the study and its important controls, but omit incidental implementation history and low-level records that do not affect interpretation or reproducibility.
* Describe exceptions together with their uniform treatment and analytical consequence. Do not hide excluded tasks, malformed outputs, non-exact categorical outputs, or unavailable dependent calls.

## Discussing Tables and Figures

When a Results section presents and discusses a table or figure, use the following paragraph structure.

### 1. Introduce the Table or Figure

* Briefly explain what the table or figure presents.
* Explain what the columns, rows, axes, or data points represent.

### 2. Discuss the Main Results

* Begin with the general, common, or central pattern shown by the data.

### 3. Discuss Specific Findings

* Continue with more specific or interesting findings observed in the data.
