# Paper Writing Guidelines

## Writing Style

* Do not use overly fancy words or overselling sentences.
* Use conservative, reviewer-safe arguments and claims.
* Be concise while providing sufficient details about the study.
* Do not enumerate examples of information, tools, signals, alternatives, or exclusions merely to make a statement sound comprehensive. When the individual items do not change the interpretation, state the relevant category at the appropriate level of abstraction.
* Prefer describing information that the study used. Mention information that was not used only when the exclusion defines an important methodological boundary, and express that boundary concisely.
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

## Citation Placement

* Place each citation immediately after the specific method, finding, or clause that it supports.
* When one sentence discusses multiple papers, attach each citation to its corresponding method or claim rather than collecting all citations at the end of the sentence.
* Group citations only when every cited source supports the same preceding claim at the same level of specificity.
* When different sources support different parts of a comparison, write separately attributable clauses or sentences so that the source-to-claim mapping remains clear.

## Auditing Background Literature

Use the following procedure whenever the Background is drafted or materially revised.

1. Inventory every citation together with the exact clause or sentence it is intended to support. Treat method descriptions, experimental conditions, findings, limitations, and comparisons as separate claims even when they appear in one sentence.
2. Verify claims against the primary paper from an official venue or author-provided manuscript. Do not rely on a title, search snippet, or secondary summary. For studies discussed in detail, inspect the relevant method, experimental setting, results, and conclusion sections rather than relying only on the abstract. For a one-sentence reference, the abstract is sufficient only when it explicitly supports every stated detail; otherwise inspect the relevant section of the paper.
3. Check each description along the dimensions that can change its interpretation: the proposed mechanism, source of feedback, training-time versus inference-time use, availability of execution or external signals, task and evaluation setting, comparison budget, and scope of the reported result. Include only dimensions that are relevant to the Background argument.
4. Preserve evidential qualifiers. Distinguish a statistically supported main result from an exploratory or secondary observation, and distinguish the authors' finding from our interpretation of its relevance. Do not generalize a result beyond the models, tasks, feedback condition, or evaluation design actually studied.
5. Give studies discussed early or in depth a correspondingly careful account of their setup, principal result, and boundary relative to this work. For later one-sentence references, state the distinctive mechanism or research scope that makes the study relevant; avoid a generic paraphrase that could apply to many papers.
6. When a source supports only part of a sentence, narrow the claim or split the sentence and place the citation after the supported clause. Correct inaccurate prose rather than merely moving citations. Do not merge properties of several papers into a composite description that no individual source supports.
7. After source-level verification, reread the Background in order to confirm that comparisons use already introduced concepts, adjacent sentences do not silently extend a cited claim, and the literature narrative remains conservative and relevant to the study's research gap.
8. Finish with a mechanical citation and build check: identify grouped citation commands and retain them only when all sources support the same claim, confirm that every citation key resolves, run `git diff --check`, and compile the paper to detect undefined citations or LaTeX errors.

## Information Order and Abbreviations

* Introduce information in the order needed by a reader who does not already know the study. Do not rely on concepts, stage names, protocol names, abbreviations, or distinctions that are defined only later.
* Before the protocol definition, discuss Research Questions using general concepts such as critique, planning, revision, selective refinement, correctness, and token use.
* After the protocol stages and notation have been defined, use those stage labels and protocol abbreviations consistently in the experimental details and results.
* Define every abbreviation before first use and make its construction unambiguous.
* Use Decision, Critique, Planning, and Revision as the four stage names, abbreviated `D`, `C`, `P`, and `R`, and concatenate the abbreviations in execution order. Thus, `CR` means Critique followed by Revision, and `CPR` means Critique followed by Planning followed by Revision. Refer to their stored outputs explicitly as a Decision label, Critique artifact, Plan artifact, or revised candidate when the distinction matters.
* Do not phrase a stage comparison as if one complete protocol were added to another. Describe the stage that is inserted or the two complete sequences being compared.
* When a spelled-out label is paired with an abbreviation, capitalize only the conceptual elements represented by the abbreviation; do not introduce unrelated capitalized words that appear to contribute additional letters.

## LaTeX Formatting

* Do not use `--` as punctuation. Use `-` only where a hyphen is grammatically required.
* In LaTeX source, place each sentence on a separate line. Do not insert a line break in the middle of a sentence or at an arbitrary point within a paragraph.
* Do not use `\paragraph{...}` headings merely to divide a sequence of methodological details. Use a clear topic sentence to establish the role of each paragraph.
* Use a `\subsubsection{...}` only when the material forms a genuinely distinct unit that readers need to locate independently.

## Writing the Study Design Section

* Open the section with two or three sentences that state the controlled study design and the scope of the section.
* Organize the main account around Research Questions, Self-Refinement Protocols, Models and Benchmarks, and Experimental Setting. Adjust these subsections only when doing so makes a substantive methodological distinction clearer.
* Avoid fragmenting the section into many narrow subsections. Use short descriptive paragraphs or structured lists within the main subsections when details need separation.
* For each Research Question, first explain why the question matters, then identify at a high level the experiment or comparison used to answer it. Leave detailed metrics and procedures to the later methodological account.
* Describe each protocol stage as an observable prompt and model call, and distinguish a stage from its artifact and from a derived protocol outcome.
* When stage composition is central to the contribution, use an overview figure to show the Shared-Initial Design, artifact flow, cumulative stage sequences, and any selection path. Do not reduce the main design to a table of stage names and inputs.
* For each central stage, explain why it is separated, what information it receives, what artifact or candidate it must produce, what it must not do, and how adding it changes the comparison being measured.
* Present the frozen prompt templates close to the corresponding stage explanation. Reproduce each complete template verbatim and in its original order, including repeated boilerplate, input wrappers, placeholders, and output contracts. Do not replace template blocks with summaries, add display-only text inside the prompt, or factor common text out of individual prompts. Prefer including the frozen source files directly, and verify their checksums against the experiment manifest before building the paper.
* Explain Planning as the operation that translates a prior Critique into an actionable edit strategy. State why it is placed after Critique, why a Planning-only sequence is not treated as the same operation, and that its measured effect includes the call, artifact, and token cost.
* Present the selected models and benchmarks in separate concise tables. Follow each table with the selection rationale, the intended coverage or comparison role, and any adopted exception that changes the final experimental scope.
* In Experimental Setting, report the procedure that was actually executed, including phase-wise execution and artifact reuse when protocols were not run independently end to end.
* Provide the hardware, software, inference parameters, evaluation environment, timeout policy, output contracts, and exception-handling rules needed to understand and reproduce the study.
* State the core methodological decision and its reason before adding implementation values or edge-case details.
* Include enough detail to explain the study and its important controls, but omit incidental implementation history and low-level records that do not affect interpretation or reproducibility.
* Describe exceptions together with their uniform treatment and analytical consequence. Do not hide excluded tasks, malformed outputs, non-exact categorical outputs, or unavailable dependent calls.

## Model and Benchmark Tables

* Follow the compact layout used in the reference refinement-gain paper rather than placing long descriptions or checkpoint identifiers in the main table body.
* The model table should use the columns `Model`, `Model category`, `Parameters`, and `Precision` unless the study requires a materially different attribute.
* Place exact checkpoint identifiers and short interpretive qualifications in table notes. Do not add a `Role` column when the selection rationale can be explained more clearly in the following prose.
* The benchmark table should use the columns `Benchmark`, `Tasks analyzed`, and `Task setting`.
* Report task counts as analyzed tasks over release tasks, and place task exclusions and their concise reasons in table notes.
* Keep evaluator versions, execution environments, and other procedural settings in Experimental Setting unless they are essential to interpreting the table itself.
* Use `threeparttable`, restrained font-size reduction, and short cells so that the tables remain readable without overflow or arbitrary mid-word wrapping.

## Discussing Tables and Figures

When a Results section presents and discusses a table or figure, use the following paragraph structure.

### 1. Introduce the Table or Figure

* Briefly explain what the table or figure presents.
* Explain what the columns, rows, axes, or data points represent.

### 2. Discuss the Main Results

* Begin with the general, common, or central pattern shown by the data.

### 3. Discuss Specific Findings

* Continue with more specific or interesting findings observed in the data.
