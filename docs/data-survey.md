# Fifteen open sources can break the count prior

The next training mix should take about 80,000 multi-answer rows from fifteen public sources with commercial-use licences, spread over fourteen task families. Options should be sampled so that the number of correct answers no longer follows from the family. Targets: about **25% empty answers**, **a third of rows with five or more answers**, **2 to 255 options**, and **30% of rows longer than 2,000 tokens**. E02 trained on mostly 1–3 answers and 8.7% empty rows. The strongest sources are:

- **QAMPARI** (CC0): mean 15 answers, up to 200.
- **Qasper** (CC BY 4.0): whole papers; 12–19% of evidence sets are empty.
- **Amazon ESCI** and **WANDS** (Apache-2.0 and MIT): human-judged product lists of up to 198 and 4,329 items.
- **Re-DocRED** (MIT): 96 relation types.
- **SQuAD 2.0**, **MuSiQue** and **Natural Questions**: natural "none" cases.
- **WiCE**: 50–200 candidate sentences per claim.
- **HUPD** patents and **arXiv**: deep label hierarchies.

A check of our own SATA file changes the held-out list. **SATA-Bench is not exam questions.** It is six task families, and every item has 2 or more answers (mean 3.6):

- MultiRC-style reading comprehension
- toxicity categories
- Reuters news topics
- MeSH headings of PubMed abstracts
- EUR-Lex concepts
- business-news event types

We recommend holding out these whole families, not only their source datasets. That removes Civil Comments, MAVEN and the multi-span reading sets from training, but it keeps the zero-shot claim that E02 pre-registered.

Public data cannot fill some gaps: "none"-heavy decisions outside legal text, many-option checks over records and logs, and open entity typing. Those gaps need labels from Apache-2.0 or MIT teachers (Qwen3, Qwen2.5 except 3B and 72B, DeepSeek-R1, Apache-licensed Mistral models, Gemma 4), never from the OpenAI, Anthropic or Gemini APIs. Huggingface.co, arXiv and the ACL Anthology were blocked during the research. About thirty licences and numbers here therefore rest on GitHub files or search extracts, and they must be re-checked before use.

*How to read the evidence. "Computed" means the research team calculated the figure on 2026-10-08 from the data file at the linked URL, or from our own benchmark file where a local path is given. "Search" means the fact comes from a search-engine extract of a page that could not be opened. "Est." means an estimate. Token counts are estimates (1.3 tokens per word, or 4 characters per token). Re-count them with the Eos tokenizer before bucketing rows by length.*

## E02 learned a count prior, so counts must stop following families

E02 trained a count head (33 outputs, counts 0 to 32) on Decision 2.0 Eos-0.8B. It used about 29,000 rows (`experiments/E02-count-head/README.md`). The multi-answer rows came from four kinds of data: GoEmotions, merged DBpedia-14 entries, our synthetic orders and the wide-probe generator. **Only 8.7% of these rows had an empty answer**, and that was after a fix following the smoke run. The model gained 27 to 78 points on its trained families but did not transfer. It failed on UNFAIR-ToS, where about nine answers in ten are empty. It also failed on SATA, whose 1,650 items average **3.61 answers and never have fewer than two** (computed from `data/bench-v0/sata.jsonl`). The simplest explanation is that the model learned how many answers its training families usually have, and then applied that number everywhere.

The literature predicts this failure, though no paper measures it directly. Held-out performance in instruction tuning grows roughly log-linearly with the number of training tasks. Examples per task matter much less:

- Super-NaturalInstructions keeps improving up to 757 tasks and saturates at about 64 examples per task ([Wang et al. 2022, search](https://arxiv.org/abs/2204.07705)).
- The Flan Collection keeps rising up to 1,836 tasks ([Longpre et al. 2023, search](https://arxiv.org/abs/2301.13688)).
- A controlled study found that the number of distinct instructions matters far more than the number of examples per instruction ([Zhang et al. 2024, search](https://arxiv.org/abs/2402.10891)).

Models also absorb the label rates of their training mix:

- Laurer's universal classifier gained 9.4% on held-out tasks from a broader task mix, but the mix made it "over- or underpredict a few classes" ([Laurer et al. 2023, search](https://arxiv.org/abs/2312.17543)).
- GLiNER trained on positives only had lower precision and more false positives. About 50% negative labels worked best ([GLiNER, search](https://arxiv.org/abs/2311.08526)).
- UniversalNER fixed missing negatives by adding absent types with empty answers ([UniversalNER, search](https://arxiv.org/abs/2308.03279)).

Two more findings shape the format:

- **LLM accuracy drops 30–50% when "None of the above" is the correct option** ([Tam et al. 2025, search](https://aclanthology.org/2025.findings-acl.1031/)). "None" must therefore be an empty answer, never an option.
- Autoregressive models that list labels one at a time "tend to suppress all but one label" ([Ma et al. 2025, search](https://aclanthology.org/2025.emnlp-main.126/)). This favours scoring each option on its own, both in our model and in our teachers.

These facts turn into concrete targets. The key change is that each source must supply several answer-count regimes, so that the count cannot be guessed from the source. The share of options that are correct matters as much as the count. In SATA, 32% to 49% of options are correct in every subset. In UNFAIR-ToS (8 options, 0–2 answers, 89% empty, per `docs/benchmark.md`), well under 5% are.

| Requirement | E02 | First-mix target |
|---|---|---|
| Task families | 4 kinds of multi-answer data | 14 public families, the E02 sources and a teacher pilot; about 30 question templates |
| Empty answers | 8.7% of rows | 25% overall; 15–45% per source; some templates at 70–90% |
| Large answers | rare | 33% of rows with 5+ answers; 7% with 20–32 |
| Answer floor | none | some templates always have 2+ answers, like SATA |
| Options per row | 4–28 (GoEmotions, DBpedia), 10–200 (wide) | log-uniform from 2 to 255 |
| Context length | mostly short | 30% over 2k tokens, 12% between 4k and 8k |
| Share of options correct | narrow | spread from under 5% to over 50% |
| Licence | includes SST-5 train, listed as "research use" | commercial-OK sources only |

One model constraint follows. The E02 count head stops at 32, so rows with more than 32 offered correct options cannot be trained with it. The first mix therefore caps the offered gold at 32. QAMPARI's 30–200-answer questions are still usable: offer a subset of their answers. Extending the head, or using the per-option sigmoid variant from the E02 ablation, would allow larger answers later.

## SATA-Bench is six task families, not exam questions

Our benchmark description calls the `sata` track "exam-style knowledge questions" (`docs/benchmark.md`). That is wrong. The SATA-Bench paper says its items span reading comprehension, news and event classification, toxicity, biomedicine and law. Its Appendix A points the reading-comprehension source to MultiRC and quotes MultiRC's design ([SATA-Bench paper, search](https://arxiv.org/pdf/2506.00643)). An inspection of our copy (SATA-Bench @371dd0c, 1,650 items) confirms six source subsets:

| Subset | Items | Task, as seen in the items | Options (mean, range) | Answers: mean (min–max) | Text words, mean | Closest public datasets |
|---|---|---|---|---|---|---|
| d1 | 342 | Reading comprehension: a story, news or science passage, a question, and candidate answers including paraphrases and Yes/No (MultiRC-style) | 5.7 (3–16) | 2.80 (2–10) | 276 | MultiRC; multi-span reading sets (DROP, Quoref, MultiSpanQA, TAT-QA) |
| d2 | 284 | Toxicity attributes of a web sentence, with label definitions in the context | 8: threat, insult, severe_toxicity, toxicity, profanity, sexually_explicit, identity_attack, flirtation | 2.56 (2–6) | 135, incl. definitions | Jigsaw and Perspective-scored sets, Civil Comments |
| d3 | 249 | Reuters-21578 news topics ("What topics are related to the document above?") | 6, from 120 codes such as acq, earn, grain | 2.37 (2–5) | 112 | Reuters-21578, RCV1, other news-topic sets |
| d4 | 260 | MeSH root categories of a PubMed abstract | 15 | 5.66 (2–11) | 207 | PubMed/MEDLINE MeSH, BioASQ Task A, OHSUMED |
| d5 | 311 | EUR-Lex concepts of an EU legal act | 15 | 5.33 (2–10) | 914 | EUR-Lex (already excluded as legal) |
| d6 | 204 | Business-news event types ("What events are related to the document above?") | 6, from 29 labels such as executive statement, m&a, funding round | 2.66 (2–5) | 558 | Source not identified; document-level event detection (MAVEN) |

All figures are computed from `data/bench-v0/sata.jsonl`.

**No SATA item has an empty answer, and every item has at least two.** SATA therefore tests a regime that E02 barely trained: many answers among few options. This has four consequences:

- **MultiRC is excluded twice.** It is the d1 source, and its CogComp "Research and Academic Use License" grants no right "to incorporate the Software into a commercial product" ([MultiRC LICENSE](https://raw.githubusercontent.com/CogComp/multirc/master/LICENSE)).
- **The held-out list must grow.** `docs/data.md` names only "SATA-Bench and UNFAIR-ToS", and E02's rule "no same-family data" now covers six families inside SATA alone.
- **d2 matches the Perspective attribute set.** Its eight attribute names are the Perspective set, and its texts are web sentences, not forum comments. My guess is that it comes from RealToxicityPrompts, but this is from memory and unverified. Civil Comments shares six of the eight attribute names (toxicity, severe toxicity, threat, insult, identity attack, sexual explicit) ([Civil Comments card](https://raw.githubusercontent.com/huggingface/datasets/2.3.0/datasets/civil_comments/README.md)), so it belongs to the same family under any rule.
- **The track's own documentation must be fixed.** Update `docs/benchmark.md` and the licence register in `docs/data.md` before E03.

## Hold out whole families, with a written boundary

E02's pre-registered rule says the held-out tracks get "no same-family data". The data plan says "whole task families (not just items) are kept out of training" (`docs/data.md`). With SATA now known to be six families, this rule can be read two ways. The choice is the user's. The table shows what each reading costs.

| | **Strict**: hold out whole families | **Loose**: hold out the source datasets and close copies |
|---|---|---|
| What is excluded | Every dataset with the same decision, the same kind of label set and the same text genre as a held-out track (boundary table below) | MultiRC; Jigsaw and Perspective-scored toxicity sets, incl. Civil Comments; Reuters-21578 and RCV1; PubMed MeSH sets; EUR-Lex and LexGLUE; NLU++, banking and hotel intent sets; CLINC150; the unidentified d6 source |
| Lost from this survey's candidates | Civil Comments, Measuring Hate Speech, HateXplain, OpenAI moderation set, MAVEN, DROP and TAT-QA multi-span, span-option templates over SQuAD 2.0 and Qasper, Re-DocRED's document-level template | Civil Comments only |
| Claim on held-out tracks | "Unseen task families", as E02 pre-registered | "Unseen datasets and label sets" |
| Effect on SATA | Measures transfer | d2 becomes close to in-domain; d1 and d6 partly |
| Coverage of the six requirements | Still met (see the mix below) | Met, with easier "none" supply and large answers |

**We recommend the strict rule**, for four reasons:

- **It is the rule E02 pre-registered.** Loosening it after seeing E02's result would weaken every zero-shot claim that follows.
- **Only the strict rule tests the fix.** E02 failed at transfer across families, so only a family-level hold-out shows whether a better count mix fixes that. Under the loose rule, a model trained on Civil Comments would see six of d2's eight label names. Its SATA score would then partly measure memory of label sets.
- **The cost is small.** The strict rule removes three useful kinds of rows: Civil Comments' "none"-heavy toxicity rows, MAVEN's large document-level answers, and DROP's small multi-span answers. Natural Questions, SQuAD 2.0, Re-DocRED pairs and WANDS replace the "none" rows. QAMPARI, ESCI and WANDS replace the large answers.
- **The loose-only sources remain usable later.** They can go into a separate "seen-family" run, reported apart. Its gap to the strict run measures how much family exposure helps, which is a useful number in itself.

The strict rule needs one written judgement: does "topic tagging" as a whole count as one family? If it does, three SATA subsets (d3, d4, d5) block every subject-tagging source. That would include DBpedia-14, which E02 already trained on. We draw the line at the same decision, the same kind of label set and the same text genre. We also propose to measure the borderline cases rather than argue about them: train the first mix with and without arXiv, HUPD, Stack Exchange and QAMPARI, and report d1, d3, d4 and d6 separately. If removing them lowers a subset's score sharply, report that subset as "unseen label set, seen task type".

The strict rule excludes the first two columns of the next table. The loose rule excludes only the source datasets and close copies named in the table above.

| Held-out track | Same family, closest | Arguably the same family | Different family: keep |
|---|---|---|---|
| SATA d1, reading comprehension with candidate answers | MultiRC, ERASER MultiRC | DROP, Quoref, MultiSpanQA, TAT-QA multi-span; span-option templates over SQuAD 2.0, Qasper and NQ; AmbigNQ; RAMDocs; teacher-made MultiRC-style statements | QAMPARI (borderline, measure it); SQuAD 2.0 "which questions does this passage answer"; evidence selection (Qasper, WiCE, MuSiQue, NQ) |
| SATA d2, toxicity attributes | Jigsaw Toxic Comment, Civil Comments, Perspective-scored text, OpenAI moderation set | Measuring Hate Speech, HateXplain targets, Civil Comments identity question, Aegis 2.0, WildGuardMix, ToxiGen, SBIC, ETHOS, BeaverTails | — |
| SATA d3, news topics | Reuters-21578, RCV1 | Any news-topic set: Wikinews, MN-DS, TweetTopic | Subject tagging of other genres: arXiv, HUPD, Stack Exchange (measure them); DBpedia-14 (already used) |
| SATA d4, MeSH headings | PubMed/MEDLINE MeSH, BioASQ Task A, OHSUMED | LitCovid, Hallmarks of Cancer; OpenAlex topics of Health and Life Sciences works; CodiEsp clinical coding | arXiv categories outside biology and medicine |
| SATA d5, UNFAIR-ToS, ECtHR (legal) | EUR-Lex and Eurlex-4K, LexGLUE, ContractNLI | ConditionalQA (gov.uk rules); patent claims | HUPD patents without the claims |
| SATA d6, business-news events | The unidentified source | MAVEN (sentence and document level), ACE, RAMS, WikiEvents, DocEE; Re-DocRED's "which relation types appear in this document" template | Re-DocRED pair- and entity-level questions |
| NLU++, CLINC150 (intents) | NLU++, CLINC150, banking77, MASSIVE, hotel intents | MIDAS dialogue acts; MetaTool; BFCL simple and multiple; tool choice from user requests (ToolLens, xLAM) | Tool or check choice from agent state, logs or records (teacher data) |

Five cases in the table need a short reason:

- **Toxicity.** Jigsaw Toxic Comment, Civil Comments, Perspective-scored text and the OpenAI moderation set ask d2's exact question: which kinds of harm does this text show? So they are the closest. Target-group questions (HateXplain, Measuring Hate Speech) ask something different: who is attacked, not what kind of harm. They are the most defensible of the rest. LLM-safety taxonomies (Aegis 2.0, WildGuardMix) differ mainly in genre: chat prompts and responses. We still recommend excluding all of them under the strict rule. d2 includes identity_attack, and these sets share texts and vocabulary with it.
- **News topics.** Any news taxonomy asks d3's question with another label list, so news-topic tagging in general is flagged as the same family. Its texts can also overlap with d6's business news.
- **Events.** Document-level MAVEN asks d6's question ("which events does this document report?") with a different label set. Sentence-level trigger detection is the same decision on a smaller unit, so it is no further away.
- **QAMPARI stays, but is flagged.** Like d1, it pairs a question with candidate answers. Unlike d1, it has no passage to read: each option comes with its own evidence sentence, and the task is set membership over entities.
- **HUPD's patent claims are dropped.** The legal exclusion names court cases, contracts and EUR-Lex, not patents. But claims are legal instruments, so we drop them as a precaution.

## Fifteen sources and an 80,000-row first mix

### The ranked shortlist

The ranking follows each source's unique contribution to what E02 lacked: large answers, "none", many options, long contexts and new families. Licence safety and label quality come next.

| # | Source | Family | What it adds | Licence (source) | Main risk |
|---|---|---|---|---|---|
| 1 | QAMPARI | List questions | 5–200 answers; 10.5% of train items have 30 or more | CC0 ([LICENSE](https://github.com/samsam3232/qampari)) | Train gold is incomplete; borderline to d1 |
| 2 | Qasper | Evidence in long papers | 2k–8k tokens; 20–200 units; 12–19% empty | CC BY 4.0 ([card](https://github.com/huggingface/datasets/blob/2.0.0/datasets/qasper/README.md)) | Some papers exceed 8k tokens |
| 3 | Amazon ESCI | Product relevance | 8–198 judged options; up to 146 correct | Apache-2.0 ([repo](https://github.com/amazon-science/esci-data)) | Prior skewed towards "relevant" |
| 4 | Re-DocRED | Relations between entities | 96 relation names; 97% of entity pairs have no relation | MIT ([LICENSE](https://github.com/tonytan48/Re-DocRED/blob/main/LICENSE)) | Document-level template excluded |
| 5 | Natural Questions | Passage choice on a full page | About 51% have no answer; pages about 8.4k tokens | CC BY-SA 3.0 ([card](https://github.com/huggingface/datasets/blob/2.0.0/datasets/natural_questions/README.md)) | MTEB lists it as non-commercial; re-check |
| 6 | SQuAD 2.0 | Which questions a passage answers | 43,498 unanswerable questions, written to look answerable | Repo MIT ([LICENSE](https://github.com/rajpurkar/SQuAD-explorer)); data licence from memory | Data licence unverified |
| 7 | MuSiQue (Ans + Full) | Multi-hop evidence | Unanswerable twin questions give clean "none" | CC BY 4.0 ([README](https://github.com/StonyBrookNLP/musique)) | Paragraph count unverified |
| 8 | HUPD | Patent classes | Long technical text; CPC hierarchy | CC BY 4.0 ([README](https://github.com/suzgunmirac/hupd)) | Over 360 GB; drop the claims |
| 9 | WANDS | Product relevance | 50–255 options; 21% of queries have no exact match | MIT ([repo](https://github.com/wayfair/WANDS)) | Only 480 queries |
| 10 | WiCE | Evidence for a claim | 50–200 sentences; up to 28 gold; about 11% empty | Annotations ODC-BY ([LICENSE](https://github.com/ryokamoi/wice/blob/main/LICENSE.md)) | Web text under Common Crawl terms; small |
| 11 | arXiv with OpenAlex labels | Scientific subjects | Hierarchy of 4,516 topics; ancestor closure gives large answers | CC0 metadata ([OpenAlex](https://help.openalex.org/data/licenses/); [Common Pile](https://arxiv.org/pdf/2506.05209)) | OpenAlex labels are machine-made; drop biomedical works |
| 12 | DBpedia-Entity v2 | Entity search | About 38 relevant among about 109 judged per query | Judgements MIT ([LICENSE](https://github.com/iai-group/DBpedia-Entity)) | Only 467 queries |
| 13 | Stack Exchange | Question tags | Many domains; tag descriptions from tag wikis | CC BY-SA ([ArchiveTeam](https://wiki.archiveteam.org/index.php/Stack_Exchange)) | Use dumps from before July 2024; tags are incomplete |
| 14 | MAMS | Review aspects | Every sentence has 2+ aspects; polarity questions add zeros | Apache-2.0 ([LICENSE](https://github.com/siat-nlp/MAMS-for-ABSA/blob/master/LICENSE)) | Only 8 options |
| 15 | CMU Movie Summary | Film genres | 42,306 plots with several genres | CC BY-SA, version unstated ([README](https://www.cs.cmu.edu/~ark/personas/data/README.txt)) | Redundant genres; deduplicate against d1's movie plots |

### The first mix

The mix holds **80,000 multi-answer rows**. It also holds **20,000 single-answer replay rows**, trained with the distillation loss as in E02, so the general track keeps its quality. The total is about 3.4 times E02. No source exceeds 9% of the multi-answer rows. "Unit selection" rows, whose options point to paragraphs or sentences in the context, stay at 22%. That follows the advice that passage options should be a minority.

| Source | Rows | Question templates | Typical answers | Empty share | Options | Context |
|---|---|---|---|---|---|---|
| QAMPARI | 8,000 | Which of these entities answer the list question? | 1–32 (half 10+) | 15% | 10–255 | 0.5k–8k, assembled |
| Qasper | 5,500 | Which paragraphs (or sentences) hold evidence? | 0–15 | 20% | 20–255 | 2k–8k |
| SQuAD 2.0 | 5,000 | Which of these questions does the passage answer? | 0–12 | 35% | 5–30 | short |
| MuSiQue | 4,500 | Which paragraphs are needed; none if insufficient | 2–4 | 25% | 20–200 | 2k–5k |
| WiCE | 2,500 | Which sentences support the claim? | 0–28 | 15% | 50–200 | 1k–4k |
| Natural Questions | 5,000 | Which passages of this page answer the question? | 0–3 | 45% | 20–200 | 2k–8k |
| ESCI | 7,000 | Exact matches / acceptable / complements | 0–32 | 20% | 8–255 | short |
| WANDS | 3,000 | Exact matches (strict) / exact or partial (lenient) | 0–32 | 25% | 20–255 | short |
| DBpedia-Entity v2 | 2,000 | Which entities are relevant to the query? | 1–32 | 15% | 20–109 | short |
| Re-DocRED | 6,500 | Relations from A to B / relations of entity A | 0–20 | 40% | 10–96 | short to 3k |
| HUPD | 5,500 | Which CPC classes or groups apply? | 1–15 | 20% | 10–255 | 1k–8k |
| arXiv with OpenAlex | 6,000 | Which arXiv categories / which topics, subfields, fields? | 1–12 | 15% | 10–255 | short |
| Stack Exchange | 3,500 | Which tags apply? | 1–5 | 20% | 5–100 | short to 1k |
| MAMS | 2,500 | Which aspects are mentioned / praised / criticised? | 0–5 | 25% | 8 | short |
| CMU Movie Summary | 3,000 | Which genres describe this film? | 1–8 | 15% | 10–200 | 0.3k–2k |
| E02 sources | 6,000 | GoEmotions, DBpedia-14 merges, orders, wide (new seeds) | 0–10 | 20% | 4–200 | short |
| Teacher pilot | 4,500 | New families (see the gaps section) | 0–32 | 40% | 2–255 | short to 8k |
| **Total** | **80,000** | about 30 templates | | **about 25%** | | |

The row-weighted empty share of this table is 24.5%. The mix should hit these aggregate targets, and the sampler should resample until each bucket is within two points of its target:

| Distribution | Buckets and target shares |
|---|---|
| Correct answers per row | 0: 25% · 1: 17% · 2–4: 25% · 5–9: 15% · 10–19: 11% · 20–32: 7% |
| Options per row | 2–4: 10% · 5–10: 20% · 11–30: 27% · 31–100: 27% · 101–255: 16% |
| Context tokens | under 512: 40% · 512–2k: 30% · 2k–4k: 18% · 4k–8k: 12% |
| Share of options correct | 5% or less: 25% · 5–20%: 30% · 20–50%: 30% · over 50%: 15% |

Some templates should keep their natural extremes. Re-DocRED pairs, the ESCI complement question and Natural Questions pages stay "none"-heavy at 50–90% empty. QAMPARI, ESCI and MAMS always have 2+ answers. Together these teach the model that the count belongs to the item, not to the family.

Replay needs one fix. E02's replay includes SST-5 train, which the E02 README lists as "research use". Replace it with a commercially licensed scoring set before any release.

### What the loose rule would add back

Under the loose rule, the mix would add:

- **MAVEN**: 7,000 rows, with document-level event types giving 5–25 answers (est.).
- **DROP and TAT-QA multi-span**: 4,000 rows, with 2–12 answers.
- **Measuring Hate Speech and HateXplain target questions**: 4,500 rows, with soft labels from annotator votes, and 38.1% "none" in HateXplain.

Civil Comments stays out under both rules, because it shares d2's label names. These rows would come out of Natural Questions, SQuAD 2.0 and Re-DocRED. We recommend training this variant only as the separate "seen-family" run described above.

## What each recommended source contains and how to convert it

Every training row has four parts: a context, a question, a list of options with short names and optional descriptions, and a gold subset. Three conversion patterns cover all fifteen sources:

- **Unit selection.** Paragraphs or sentences are numbered inside the context. Each option is a short label such as "Paragraph 12 (Section 3.2, Model)", with the first words of that paragraph as its description.
- **Exhaustive label inventories.** All gold labels are offered together with sampled distractors.
- **Judged candidate lists.** Every option is a judged item.

In all three patterns, **the gold answer is the set of offered options that are correct**. A "none" row is an option list that contains no correct option. It is never a "None of these" option.

### Lists and answerability: QAMPARI and SQuAD 2.0

| Source | One item | Train size | Answers: mean / max / empty | Text | Annotation | Licence |
|---|---|---|---|---|---|---|
| QAMPARI | A question about a Wikipedia entity, plus answers, each with aliases, a URL and a proof sentence | 61,911 train; 1,000 dev; 1,000 test | 15.1 / 200 / 0%; median 8; 18.2% have 20+; 10.5% have 30+ ([computed](https://aggreg-qa.s3.amazonaws.com/qampari.zip)) | Proof sentences, mean 24 words | Train generated automatically from Wikidata and tables; dev and test written and checked by people ([README](https://github.com/samsam3232/qampari)) | CC0 1.0; proof text is Wikipedia, CC BY-SA |
| SQuAD 2.0 | A Wikipedia paragraph with several questions; each unanswerable one has `plausible_answers` | 130,319 questions over 19,035 paragraphs; 43,498 (33.4%) unanswerable | 6.85 questions per paragraph; 153 paragraphs have only unanswerable questions ([computed](https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/train-v2.0.json)) | One paragraph | Crowd-written | Repo MIT ([LICENSE](https://github.com/rajpurkar/SQuAD-explorer)); data CC BY-SA 4.0 from memory, unverified |

**QAMPARI** is the only large source of 10–200-answer items with a clean licence. About 11,300 train questions have 20 or more answers, and about 6,500 have 30 or more (derived from the computed shares). Its question kinds are wikidata_simple (28,574), wikidata_comp (25,200), wikitables_composition (5,836) and wikidata_intersection (2,301) ([computed](https://aggreg-qa.s3.amazonaws.com/qampari.zip)).

To convert it, the options are entity names: the offered gold answers plus distractors. The context is a shuffled list of short facts: the proof sentence for each offered gold answer, and one sentence per distractor that shows it fails the relation (for example, a manga by a different artist). At about 24 words per option, 200 options fit in about 8k tokens (est.).

- A "none" row offers only distractors and removes the gold proofs.
- Large-answer rows come from questions with 20 or more answers, capped at 32 offered gold.
- Large-option rows add distractors up to 255.

The main risk is incomplete gold. The authors had an expert add missing answers to 200 test questions, which shows the gold lists were known to be incomplete ([README](https://github.com/samsam3232/qampari)). So **never pick a distractor just because it has the right type and is not in the gold list**. Use one of three kinds instead:

- entities whose own evidence contradicts the relation;
- gold answers of a sibling question with a different relation;
- sampled distractors that two teachers have checked.

Keep dev and test, which people checked, for our own validation.

**SQuAD 2.0** gives the cheapest natural "none". Use only the answerability template: "Which of these questions does the passage answer?" The options are the paragraph's 5–15 questions, plus questions from other paragraphs of the same article for more options and more zeros. The gold answer is the answerable subset. The unanswerable questions were written to look answerable, so they are hard negatives. Under the strict rule, drop the span-option template, because it reproduces d1. Hash every paragraph against BoolQ: both datasets use Wikipedia passages, so passage overlap is possible even though question overlap is not expected.

### Evidence selection in long documents: Qasper, WiCE, MuSiQue and Natural Questions

| Source | One item | Train size | Gold units: mean / max / empty | Candidate units | Text | Annotation | Licence |
|---|---|---|---|---|---|---|---|
| Qasper | A full NLP paper plus questions; each answer has evidence paragraphs, highlighted sentences, or an "unanswerable" flag | 888 papers / 2,593 questions | 1.43 / 21 (37 in dev) / 12–19% empty, depending on whether you count the first or all annotations | Median 43–46 paragraphs (max 526–644); about 171 sentences | Mean 3,712 words; p90 estimated at 7.2k–9.1k tokens | NLP practitioners wrote and answered the questions; v0.3 fixed 0.6% of conflicts ([tarball](https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz)) | CC BY 4.0 |
| WiCE | A Wikipedia claim, the sentences of its cited web page, and every valid supporting set | 1,260 claims (plus subclaims) | Union of sets 3.5–4.2 / 28 / about 10.8% empty | Median 83 sentences; 65% of claims have 50–200 ([computed](https://github.com/ryokamoi/wice/tree/main/data/entailment_retrieval/claim)) | Median about 1.3k–1.6k tokens; p90 about 4k | Crowd; marks every valid supporting set | Annotations ODC-BY; text Wikipedia CC BY-SA and Common Crawl terms |
| MuSiQue | A 2–4-hop question over paragraphs with `is_supporting` flags; the Full version adds unanswerable twins | 19,938 train ([search](https://huggingface.co/datasets/dgslibisey/MuSiQue/tree/main)) | 2–4 supporting paragraphs | Reported 20 paragraphs (unverified) | About 2k–3k tokens (est.) | Composed from single-hop questions to resist shortcuts ([paper, search](https://arxiv.org/abs/2108.00573)) | CC BY 4.0 |
| Natural Questions | A question plus a whole Wikipedia page with long-answer candidates (paragraphs, lists, tables) | 307,373 | 0–1 in train (5 annotations in dev); about 51% have no long answer ([search](https://arxiv.org/abs/1901.08634)) | Tens to hundreds of candidates per page (est.) | About 8.4k tokens per page on average ([search](https://arxiv.org/abs/2010.09692)) | One annotator in train, five in dev ([README](https://github.com/google-research-datasets/natural-questions/blob/master/README.md)) | CC BY-SA 3.0 per card; MTEB lists CC BY-NC-SA 3.0 |

**Qasper** is the best single source of real long contexts with many natural options and native "none". To convert it, number every paragraph and every figure or table caption, and ask "Which paragraphs contain evidence needed to answer: …?" Use the union of all annotators' evidence as gold. "None" comes from unanswerable questions and empty evidence. For 100–255 options, switch to sentence mode, using `highlighted_evidence` as gold. For papers above 8k tokens, keep the gold paragraphs and a contiguous neighbourhood. Under the strict rule, drop the extractive-span template.

**WiCE** is small but already in the target shape. Ask "Which sentences of this page support the claim?" The gold answer is the union of the valid sets, and not_supported claims give empty sets. Pad items below 50 sentences with sentences from another claim's page, and cut the rare items above 8k tokens around the gold.

**MuSiQue** gives contrast pairs. Ask "Which paragraphs are needed to answer the question? Select none if the context is not enough." MuSiQue-Full's unanswerable twins give "none" rows that differ from answerable rows by a small edit in the context. That is exactly the signal a count head needs. MuSiQue publishes the IDs of single-hop questions that also occur in SQuAD and NQ dev or test sets ([README](https://github.com/StonyBrookNLP/musique)). Use them to deduplicate across our own sources.

**Natural Questions** is the largest "none" supply over long pages. Keep the page's top-level candidates, cut the page to 8k tokens, and drop items whose gold falls outside the window. Its licence conflict must be resolved first (see the facts to re-check).

### Human-judged relevance lists: ESCI, WANDS and DBpedia-Entity v2

| Source | One item | Size | Correct per item: mean / max / empty | Judged options per item | Annotation | Licence |
|---|---|---|---|---|---|---|
| Amazon ESCI | A shopping query plus result products, each labelled Exact, Substitute, Complement or Irrelevant | 130,652 queries, 2.62M judgements; US large train 74,888 queries; 3 locales | Exact 13.1 / 146 / under 0.05%; 24.9% of queries are all Exact ([computed](https://media.githubusercontent.com/media/amazon-science/esci-data/main/shopping_queries_dataset/shopping_queries_dataset_examples.parquet)) | 8–198, mean 20.1 | "Manually annotated" ([README](https://github.com/amazon-science/esci-data)) | Apache-2.0 |
| WANDS | A furniture query plus judged products, labelled Exact, Partial or Irrelevant | 480 queries, 42,994 products, 233,448 labels | Exact 53.4 (median 10) / 878 / 21% zero Exact ([computed](https://raw.githubusercontent.com/wayfair/WANDS/main/dataset/label.csv)) | 1–4,329, median 216.5 | Human, with published guidelines ([README](https://github.com/wayfair/WANDS)) | MIT |
| DBpedia-Entity v2 | An entity-search query (named-entity, keyword, natural-language and list queries) plus DBpedia entities graded 0/1/2 | 467 queries; over 49,000 judgements | About 38 relevant per query | About 109 judged per query ([ir_datasets](https://github.com/allenai/ir_datasets/blob/master/ir_datasets/etc/metadata.json)) | Crowd, with expert review of disagreements ([README](https://github.com/iai-group/DBpedia-Entity)) | Judgements MIT; DBpedia text CC BY-SA (unverified) |

**ESCI** is the best permissive source of many correct options among judged candidates. Option text is the product title, brand and first bullet, cut to about 40 tokens. Use three questions per query:

- "Which products match exactly?" (gold: Exact)
- "Which are acceptable?" (gold: Exact or Substitute)
- "Which would complement this purchase?" (gold: Complement; often empty)

Its prior is skewed: almost no query lacks an Exact item. For "none" rows, use options labelled only Irrelevant or Complement, available for the 21.2% of queries with 3 or more Irrelevant items, or pad with products from a different leaf category. For 100–255 options, add 50–150 cross-category products.

**WANDS** supplies the largest natural option lists and the largest answers. Subsample each query to 20, 50, 100 or 255 options, stratified so that the share of Exact items varies. Its 21% of queries without an Exact product give native "none" rows. It has only 480 queries, so cap the rows per query and keep each query's rows in one split.

**DBpedia-Entity v2** adds open-domain entity lists. Its list-search and natural-language queries have many correct entities. Options are the entity name plus the first sentence of its abstract. Use only judged entities as options, because an unjudged entity is not a confirmed negative.

### Relations, aspects and genres: Re-DocRED, MAMS and CMU Movie Summary

| Source | One item | Size | Answers | Options | Annotation | Licence |
|---|---|---|---|---|---|---|
| Re-DocRED | A Wikipedia document with entities and relation triples over 96 Wikidata relations | 3,053 / 500 / 500 documents; 28.1–34.9 triples per document ([README](https://github.com/tonytan48/Re-DocRED)) | Pairs: in DocRED, 97.1% of entity pairs have no relation ([DocRED paper](https://arxiv.org/pdf/1906.06127)), and at least ~7% of related pairs have several ([search](https://arxiv.org/pdf/2507.22926)) | 96 relation names | Re-annotation of DocRED to fix false negatives and logic errors | MIT |
| MAMS (category version) | A restaurant review sentence with aspect categories and polarities | 3,149 train sentences | Mean 2.25, max 5, 0% empty, 100% have 2+ ([computed](https://github.com/siat-nlp/MAMS-for-ABSA/tree/master/data/MAMS-ACSA/raw)) | 8 categories | Not retrieved | Apache-2.0 |
| CMU Movie Summary | A Wikipedia plot summary plus Freebase genres | 42,306 summaries | About 3–4 genres (est.) | About 360 genres (est.) | Freebase; noisy and redundant | CC BY-SA, version unstated ([README](https://www.cs.cmu.edu/~ark/personas/data/README.txt)) |

**Re-DocRED** works well for both ends of the count range.

- **Pair level:** "Which relations hold from «Head» to «Tail»?" with 10–96 relation names. This is naturally a "none"-heavy question; down-sample the empty pairs to the template target. DocRED documents average 196.7 words and 19.5 entities ([DocRED paper](https://arxiv.org/pdf/1906.06127)).
- **Entity level:** "Which relations does «Entity» take part in as head?" This gives larger answers.
- Under the strict rule, drop the document-level "which relation types appear here?" question, which resembles d6.
- Use Re-DocRED, not DocRED, for gold. DocRED's false negatives would turn true relations into wrong negatives.
- Give each relation a description: map the Wikidata property IDs to labels, and have a teacher write one-line descriptions.

**MAMS** guarantees 2 or more aspects per sentence. The polarity questions ("Which aspects are criticised?") naturally give zeros. **CMU Movie Summary** adds narrative text and a genre family. Merge redundant genres ("Drama" and "World cinema") first, and deduplicate the plots against d1, which contains movie-plot passages.

### Taxonomy tagging outside the held-out genres: HUPD, arXiv with OpenAlex, and Stack Exchange

| Source | One item | Size | Labels per item | Label inventory | Text | Licence |
|---|---|---|---|---|---|---|
| HUPD | A US patent application with 34 fields, including title, abstract, claims, description, `cpc_labels` (list) and `ipcr_labels` (list) | 4,518,263 applications filed 2004–2018; over 360 GB ([README](https://github.com/suzgunmirac/hupd)) | Several codes (mean not found) | CPC hierarchy, sections down to groups | Often far above 8k tokens; cut to fit | CC BY 4.0 (GitHub); one hint says the HF card shows CC BY-SA 4.0 |
| arXiv metadata | Title, abstract, `categories`, licence | About 1.7M at the 2020 launch, more now ([search](https://hyper.ai/en/news/13084)) | About 1.5–2 (est.) | About 150 categories (est.) | Abstract | CC0 for metadata ([HF loader](https://huggingface.co/datasets/arxiv-community/arxiv_dataset/blame/refs%2Fpr%2F4/arxiv_dataset.py)) |
| OpenAlex topics | Up to 3 topics per work, plus subfield, field and domain | Joined to arXiv works | Up to 3 topics, plus their ancestors | 4 domains → 26 fields → 252 subfields → 4,516 topics, named and described by an LLM ([topics](https://help.openalex.org/data/topics/)) | — | CC0 metadata; the grant covers metadata only ([UU guide](https://libguides.library.uu.nl/openalex)) |
| Stack Exchange | A question title and body, plus tags | Tens of millions (est.) | 1–5 tags (est.) | Each site's tag vocabulary with tag-wiki excerpts | About 100–400 words (est.) | CC BY-SA 2.5, 3.0 or 4.0 by post date |

**HUPD** is the only clean source with millions of long technical documents and expert multi-code labels. Ask "Which technology classes does this application belong to?" Options are CPC subclass or group titles, with distractors from sibling classes. Gold is `cpc_labels` mapped to the chosen level. There are no natural zeros, so "none" rows offer only classes from other sections. Use title, abstract, summary and description, and leave out the claims. Start from a slice of filing years, because the full set exceeds 360 GB.

**arXiv with OpenAlex labels** gives large option lists and large answers through ancestor closure. If a paper is in "Quantum Physics" and "Physics" is also offered, both are gold.

- Take the text from the CC0 arXiv metadata, not from OpenAlex. OpenAlex ships abstracts only as an inverted index "because of legal constraints" ([work object](https://docs.openalex.org/api-entities/works/work-object)).
- OpenAlex topics are machine-assigned. The reported accuracy is 0.53 top-1 and 0.73 top-3, from an unpinned source ([classifier repo](https://github.com/ourresearch/openalex-topic-classification)). So keep only high-scoring topics, and use distant distractors for "none".
- Under the strict rule, drop works in the Health Sciences and Life Sciences domains, because they resemble d4.

**Stack Exchange** adds user-written questions, code and about 180 sites (est.). Only the dumps released up to April 2024 avoid the July 2024 click-through, which reserves the file "for projects that do not include training a large language model" ([DevClass](https://devclass.com/2024/07/30/stack-exchange-restricts-access-to-dump-of-user-contributed-data-as-critics-complain-license-permits-reuse-for-any-purpose)). Authors often omit tags, so "none" rows need semantically distant distractors.

### Reserve sources, and sources usable only under the loose rule

| Source | Status | Key facts | Licence |
|---|---|---|---|
| HotpotQA and 2WikiMultiHopQA | Reserve (same family as MuSiQue) | 90,447 and 167,454 train items with supporting sentences; 2–4 gold; a single-hop model reaches 67 F1 on HotpotQA ([search](https://arxiv.org/abs/1906.02900)) | CC BY-SA 4.0 ([README](https://github.com/hotpotqa/hotpot/blob/master/README.md)); Apache-2.0 ([repo](https://github.com/Alab-NII/2wikimultihop)) |
| MIRACL | Reserve | 16 languages, 40,203 train queries, about 8.5 judged and 2–3 relevant per query | Apache-2.0 ([repo](https://github.com/project-miracl/miracl)) |
| TyDi QA | Reserve | Passage choice or NULL in 11 languages; 166,916 train | Apache-2.0 ([README](https://github.com/google-research-datasets/tydiqa/blob/master/README.md)) |
| FEVER | Reserve | 185,445 claims; evidence often incomplete ([search](https://arxiv.org/abs/1811.10971)) | CC BY-SA 3.0, but the card also tags gpl-3.0 ([card](https://github.com/huggingface/datasets/blob/2.0.0/datasets/fever/README.md)) |
| SciDocs | Reserve | 30 candidates, about 5 relevant | CC BY 4.0 ([repo](https://github.com/allenai/scidocs)) |
| XED | Reserve (same family as GoEmotions, which is in-domain) | 8 emotions; mean 1.28; plus 9,674 neutral lines for "none" ([computed](https://raw.githubusercontent.com/Helsinki-NLP/XED/master/AnnotatedData/en-annotated.tsv)) | CC BY 4.0 ([card](https://raw.githubusercontent.com/huggingface/datasets/2.3.0/datasets/xed_en_fi/README.md)) |
| CodiEsp | Reserve (borderline to d4) | 1,000 Spanish clinical cases, about 18 ICD-10 codes each ([search](https://arxiv.org/pdf/2308.02199)) | CC BY 4.0 per a catalogue only ([ODESIA](https://portal.odesia.uned.es/en/node/82)) |
| MAVEN | Loose rule only (d6 family) | 4,480 documents, 168 event types, 118,732 mentions, annotated negative triggers ([paper](https://arxiv.org/pdf/2004.13590)) | MIT repo ([LICENSE](https://github.com/THU-KEG/MAVEN-dataset/blob/main/LICENSE)); data hosted elsewhere |
| DROP and TAT-QA multi-span | Loose rule only (d1 family) | 4,698 and 1,645 train multi-span questions; 2–12 spans | CC BY-SA 4.0 ([zip](https://ai2-public-datasets.s3.amazonaws.com/drop/drop_dataset.zip)); CC BY 4.0 ([README](https://github.com/NExTplusplus/TAT-QA)) |
| Civil Comments, Measuring Hate Speech | Civil Comments: excluded under both rules. MHS: loose rule only | 1.8M comments with 7 rater-fraction attributes; MHS 39,565 comments with 135,556 annotator rows | CC0 ([card](https://raw.githubusercontent.com/huggingface/datasets/2.3.0/datasets/civil_comments/README.md)); CC BY 4.0 ([search](https://huggingface.co/datasets/ucberkeley-dlab/measuring-hate-speech/blob/5a51cae348dfc2f4e0be3eee1865b8f10e39c83e/README.md?code=true)) |
| HateXplain, OpenAI moderation set | Strict rule: excluded (d2 family). Loose rule: HateXplain targets allowed; skip OpenAI moderation, which asks d2's question | HateXplain targets: 38.1% none; OpenAI: 44.6% none among fully labelled items | MIT ([LICENSE](https://github.com/hate-alert/HateXplain/blob/master/LICENSE), [repo](https://github.com/openai/moderation-api-release)) |
| xLAM function-calling 60k | Reserve (close to intents) | Generated by DeepSeek-V2-Chat and Mixtral-8x22B; gated | CC BY 4.0 per a mirror ([card](https://huggingface.co/datasets/shumi2011/function1/blob/main/README%20(10).md)) |

## About sixty sources fail the licence test or need an email first

A commercial open-weights release rules out the following sets. Each is ruled out by its own licence or terms of use.

| Source | Problem | Evidence |
|---|---|---|
| MultiRC | Research and academic use only; also the d1 source | [LICENSE](https://raw.githubusercontent.com/CogComp/multirc/master/LICENSE) |
| RoMQA | CC BY-NC 4.0 | [README](https://github.com/facebookresearch/romqa) |
| BeaverTails, PKU-SafeRLHF | CC BY-NC 4.0 | [README](https://github.com/PKU-Alignment/beavertails), [card](https://huggingface.co/datasets/PKU-Alignment/PKU-SafeRLHF/blob/f4b036fc262da341565c0d01b2e8cf47d386921e/README.md) |
| MAVE | CC BY-NC 4.0 | [LICENSE](https://github.com/google-research-datasets/MAVE/blob/master/LICENSE) |
| MS MARCO and everything built on it (TREC DL, TREC RAG 2024/25, parts of CAsT) | "Non-commercial research purposes only" | [repo](https://github.com/microsoft/msmarco) |
| Multi-News, ASNQ | Non-commercial (ASNQ's README and LICENSE disagree) | [card](https://github.com/huggingface/datasets/blob/2.0.0/datasets/multi_news/README.md), [LICENSE](https://github.com/alexa/wqa_tanda/blob/master/LICENSE) |
| MovieLens, MIND, Goodreads | Research or academic use only | [MovieLens](https://sinbad2.ujaen.es/git/admin/py-grex/src/branch/main/datasets/ml-100k/README), [MIND](https://www.microsoft.com/en-us/research/academic-program/mind-news-recommendation-challenge/faq/), [Goodreads](https://mcauleylab.ucsd.edu/public_datasets/gdrive/goodreads/UCSD%20Book%20Graph.html) |
| OHSUMED | CC BY-NC 4.0 (also d4 family) | [card](https://huggingface.co/datasets/community-datasets/ohsumed/raw/a6159aa953215abfee43271ed0783e105d81de3b/README.md) |
| SwDA, DailyDialog | CC BY-NC-SA (also dialogue) | [SwDA](https://raw.githubusercontent.com/huggingface/datasets/2.3.0/datasets/swda/README.md), [DailyDialog](https://raw.githubusercontent.com/huggingface/datasets/2.3.0/datasets/daily_dialog/README.md) |
| CARER, SemEval-2021 Task 6, ToxiGen | Research or educational use only | [CARER](https://github.com/dair-ai/emotion_dataset), [Task 6](https://github.com/di-dimitrov/SEMEVAL-2021-task6-corpus), [ToxiGen](https://github.com/microsoft/TOXIGEN) |
| ETHOS | GPL-3.0 / AGPL (copyleft) | [card](https://raw.githubusercontent.com/huggingface/datasets/2.3.0/datasets/ethos/README.md) |
| RCV1, Reuters-21578 | Signed agreements; "research purposes only" (UCI's CC BY 4.0 label conflicts); also d3 family | [NIST](https://trec.nist.gov/data/reuters/reuters.html), [README](https://ics.uci.edu/~kdd/databases/reuters21578/README.txt) |
| DeliciousT140, BioASQ | Research only; NLM terms with registration | [zubiaga.org](https://www.zubiaga.org/datasets/delicioust140/), [BioASQ](https://participants-area.bioasq.org/datasets) |

The following sets have no usable licence statement, or conflicting statements. The **bold** ones are worth one email to the authors, because they are dense and fit a family that the strict rule keeps:

| Source | What is unclear | Why it matters |
|---|---|---|
| **QUEST** | Only code and models are "Apache 2.0" ([README](https://github.com/google-research/language/tree/master/language/quest)) | Set operations including negation; at most 20 answers |
| **Ultra-Fine Entity Typing** | No licence found; part of the data is LDC Gigaword ([README](https://github.com/uwnlp/open_type)) | 10,331 types, about 5 gold per mention |
| **SemEval-2020 Task 11 and 2023 Task 3 (persuasion techniques)** | "Unknown" or registration-gated ([card](https://raw.githubusercontent.com/huggingface/datasets/2.3.0/datasets/sem_eval_2020_task_11/README.md)) | Long news articles with 14–23 techniques. The texts are news, so check them against d3 and d6 |
| **SemEval ABSA 2014–16** | No stated licence ([TIB](https://service.tib.eu/ldmservice/dataset/91b01933-994d-4672-ac46-0545c5e411cd)) | Laptop entity–attribute categories give many options |
| MultiSpanQA | No LICENSE file ([repo](https://github.com/haonan-li/MultiSpanQA)) | Exactly one third none, one third single, one third multi; but d1 family under the strict rule |
| Quoref, MASH-QA, ComplexWebQuestions, HoVer, IIRC, WikiQA, LongCite-45k, QMSum | Missing or conflicting statements | Lower value or covered by other sources |
| SciFact | LICENSE.md says claims CC BY 4.0; the HF card and MTEB say non-commercial | [LICENSE](https://github.com/allenai/scifact/blob/master/LICENSE.md), [card](https://huggingface.co/datasets/allenai/scifact) |
| ConditionalQA | BSD-2 file, but the README says "ONLY ... NLP research"; also gov.uk rules | [README](https://github.com/haitian-sun/ConditionalQA) |
| Aegis 2.0, BRIGHTER, Touché23-ValueEval | CC BY 4.0 reported but not confirmed on the live cards; Aegis is also d2 family | [Aegis paper](https://arxiv.org/pdf/2501.09004), [Touché](https://huggingface.co/datasets/webis/Touche23-ValueEval) |
| FrameNet, FIGER, SBIC, TweetTopic, MPST, BGC, AmbigNQ | Custom or unknown terms | FrameNet frames are close to event detection (d6) |

Some sets have a permissive licence but were made with a model whose terms forbid training a competing model, or they bind the release:

- **OpenAI models:** ToolBench, MetaTool, Seal-Tools, HAGRID, NuNER, Pile-NER (also CC BY-NC), GLiNER2's data, GLiClass's GPT-4o stream, s2_fos labels and Amazon-C4 ([OpenAI terms](https://openai.com/policies/row-terms-of-use/)).
- **Llama 3 8B:** Knowledgator's multi-task data. The Llama 3 licence bans using outputs "to improve any other large language model" ([Llama 3 LICENSE](https://github.com/meta-llama/llama3/blob/main/LICENSE)).
- **Llama 3.1:** WebOrganizer's annotations. The licence binds the name of any released model trained on them, which must start with "Llama" ([Llama 3.1 LICENSE](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)).

Before any row is used, the licence register in `docs/data.md` needs a line for every source, as the data plan requires.

## Seven curation steps, each tied to evidence

| Step | Setting we propose | Evidence |
|---|---|---|
| 1. Licence and provenance gate | One register line per source; every row stores source, licence, generator and template | `docs/data.md` principle 3 |
| 2. Deduplication | Exact plus MinHash near-duplicates, within and across sources, on context and on (context, question) | Deduplication cut memorised output about 10×, and found more than 4% train–test overlap in standard validation sets ([Lee et al. 2022, search](https://aclanthology.org/2022.acl-long.577)) |
| 3. Decontamination | Drop any row that shares a 13-gram, or has a high embedding similarity, with any item of benchmark v0 or of the held-out source datasets | GPT-3 and lm-eval-harness 13-gram rule ([doc mirror](https://huggingface.co/koichi12/llm-scripts/blob/main/scripts/yans/lm-evaluation-harness/docs/decontamination.md)) |
| 4. Clean negatives | Use only judged or in-document negatives; check distractors from incomplete lists with two teachers; run multi-label cleanlab after a first model | Laurer removed about 150k noisy texts with cleanlab ([repo](https://github.com/MoritzLaurer/zeroshot-classifier)); multi-label confident learning ([Thyagarajan et al., search](https://arxiv.org/abs/2211.13895)) |
| 5. Mixing caps | At most 9% of rows per source; at most 3 option-sampled variants per base item; at most 2 passes over small sources; temperature sampling, as in the data plan | FLAN capped each dataset at 30k with a 3k mixing maximum ([search](https://arxiv.org/abs/2109.01652)); SNI saturates at 64 per task; UniMax caps repeats ([search](https://arxiv.org/abs/2304.09151)) |
| 6. Option sampling | K log-uniform in 2–255; gold count drawn to fill the target buckets; distractors one third random, two thirds hard (siblings, nearest labels), drawn in proportion to label frequency; option order shuffled; names paraphrased and descriptions added for about 40% of rows | Frequency-based negatives ([UniversalNER, search](https://arxiv.org/abs/2308.03279)); about 50% negatives ([GLiNER, search](https://arxiv.org/abs/2311.08526)); position bias ([PriDe, search](https://arxiv.org/abs/2309.03882)); label descriptions add 17–19 points ([Gao et al., search](https://aclanthology.org/2023.emnlp-main.853)) |
| 7. Count audit and reporting | A small classifier that predicts the count bucket from source and template alone must stay near chance; report every evaluation by count bucket and by share of options correct | Laurer's over- and under-prediction under a task mix ([search](https://arxiv.org/abs/2312.17543)) |

**Decontamination** has to cover more than the test splits named in the brief. Benchmark v0 evaluates BoolQ and HellaSwag on their *validation* splits, so those splits are the ones to remove (`docs/benchmark.md`). The full list:

- every benchmark v0 track: sata, goemotions test, unfair_tos, nlupp, ecthr, synthetic seed 0 and wide seed 0;
- the general track: MMLU-Pro test, BBH (including its canary string), ANLI test r1–r3, HellaSwag validation, CLINC150 test and out-of-scope, BoolQ validation, SST-5 test;
- whole source datasets of the held-out families: MultiRC, Reuters-21578, EUR-Lex, LexGLUE, NLU++, and the Jigsaw and Civil Comments sets.

E02 dropped rows whose state appears in benchmark v0 (`experiments/E02-count-head/README.md`). The 13-gram and embedding checks also catch near copies that an exact match misses. Three passage-level checks deserve care:

- CMU Movie Summary plots against d1's movie passages.
- Wikipedia paragraphs against BoolQ.
- Any web text used for teacher contexts against d2's web sentences and d6's company news pages.

Also exclude whole datasets that hide evaluation items: DocNLI reuses ANLI premises ([search](https://arxiv.org/abs/2106.09449)). Laurer's v1 mix and tasksource contain banking77 and MASSIVE ([repo](https://github.com/MoritzLaurer/zeroshot-classifier), [tasksource](https://github.com/sileod/tasksource)).

**Clean negatives** decide whether the count signal is trustworthy, because a false negative teaches the model to under-select. The rule depends on how a source was annotated:

- **In-document units** (Qasper paragraphs, WiCE sentences, MuSiQue paragraphs) were read by the annotator, so unselected units are reliable negatives. FEVER is the counter-example: its own organisers found evidence "was often incomplete" ([search](https://arxiv.org/abs/1811.10971)).
- **Judged lists** (ESCI, WANDS, DBpedia-Entity) are safe only within the judged items.
- **Author tags and generated lists** (Stack Exchange, arXiv cross-lists, OpenAlex, QAMPARI train) need distant distractors or a teacher check.

Measure the false-negative rate of sampled distractors on 200 items per source before scaling up. The research did not measure it for any source.

**Soft targets** can replace hard labels where the source gives graded or multiple judgements: ESCI's Substitute class, WANDS Partial, DBpedia grade 1, and multiple Qasper or WiCE annotations. The proper set loss used in E02 can fit them directly.

**A test-time prior adapter** is a fallback, not a substitute for a good mix. Contextual calibration improved GPT-3 accuracy by up to 30 points ([Zhao et al. 2021, search](https://proceedings.mlr.press/v139/zhao21c.html)), and an EM prior correction "is hard to beat" for label shift ([Alexandari et al., search](https://arxiv.org/abs/1901.06852)). But no method is validated for multi-label zero-shot models, so test any adapter on the dev split of each track only.

## Teachers must fill five gaps, and only open teachers qualify

The strict rule and the licence filter leave four gaps that no public dataset fills, and a fifth need: more families.

| Gap | Why public data fails | Teacher recipe | Pilot rows |
|---|---|---|---|
| "None"-heavy decisions with few options outside legal, toxicity and news text (UNFAIR-ToS-like rates) | After the strict rule, natural "none" comes only in retrieval and relation shapes | Records, logs, recipes, product specs or meeting notes, each with 6–12 described checks ("Which of these data-quality problems does this record have?"); 60–80% empty by design | 1,500 |
| Many-option checks with large answers in long, non-Wikipedia contexts | Only QAMPARI, ESCI and WANDS reach 20+ answers, and none of them are long technical texts | "Which of these 50–255 requirements does this specification meet?" or "Which tests does this change affect?", over generated documents up to 8k tokens | 2,000 |
| Open entity typing with many types | Pile-NER is CC BY-NC and GPT-made ([repo](https://github.com/universal-ner/universal-ner)); UFET's licence is unknown | Re-create "which of these types apply to the marked entity" with open teachers over permissively licensed text such as Common Pile | 1,000 |
| Verified distractors and option descriptions for public sources | QAMPARI gold is incomplete; Wikidata and CPC labels lack descriptions | Per-option yes/no checks by two teacher families; one-line descriptions and paraphrased names | labels only |
| More families overall | 14 public families sit far below the hundreds of task types where transfer grows ([Longpre et al., search](https://arxiv.org/abs/2301.13688)) | Grow to 30–50 teacher families across E03 and E04, built with attribute-diversified prompts ([AttrPrompt, search](https://arxiv.org/abs/2306.15895)) | from E03 on |

**Teacher data must not recreate a held-out family.** It must contain no toxicity or harm categories, no news topics or news events, no medical subject headings, no reading comprehension with candidate answers, no legal texts, and no intents in customer messages. Tool or check selection is acceptable only over agent state, logs or records, never over user requests. That form would sit too close to NLU++ and CLINC150.

**Which teachers are allowed** depends on the model licence and on the hosting provider's terms. The data plan already requires both checks and at least two teacher families (`docs/data.md`).

| Teacher | Status | Terms | Evidence |
|---|---|---|---|
| Qwen3 (all sizes) | Allowed, verify | Reported Apache-2.0 for all models | Secondary source ([IntuitionLabs](https://intuitionlabs.ai/articles/open-weight-ai-model-licenses)) |
| Qwen2.5, except 3B and 72B | Allowed | Apache-2.0 | [Qwen2.5 blog, search](https://qwenlm.github.io/blog/qwen2.5/) |
| DeepSeek-R1 | Allowed | MIT; "API outputs can now be used for fine-tuning & distillation"; distilled versions inherit their base licence (avoid the Llama-based 70B) | [card](https://huggingface.co/deepseek-ai/DeepSeek-R1), [release note](https://api-docs.deepseek.com/news/news250120) |
| Mixtral and other Apache-licensed Mistral models | Allowed | "Most" open Mistral models are Apache-2.0; Mistral Large 2 is research-only; Codestral is non-production | [Mistral help](https://help.mistral.ai/en/articles/347393-under-which-license-are-mistral-s-open-models-available), [Willison](https://simonwillison.net/2024/Jul/24/mistral-large-2) |
| Gemma 4 | Allowed, verify | Apache-2.0, released 31 March 2026 | [release page, search](https://ai.google.dev/gemma/docs/releases?hl=zh-CN) |
| gpt-oss | Allowed after reading its usage policy | Apache-2.0 plus a USAGE_POLICY file not yet read | [repo](https://github.com/openai/gpt-oss) |
| Qwen2.5-72B | Conditional | Must display "Built with Qwen" or "Improved using Qwen" | [discussion, search](https://huggingface.co/Qwen/Qwen2.5-72B-Instruct/discussions/18) |
| Llama 3.1, Llama 4 | Avoid | The released model's name must begin with "Llama" | [Llama 3.1 LICENSE](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE) |
| Llama 3.0; Gemma 1–3 | Not allowed | Llama 3 bans improving other LLMs; Gemma terms treat models trained on Gemma outputs as "Model Derivatives" | [Llama 3 LICENSE](https://github.com/meta-llama/llama3/blob/main/LICENSE), [Gemma terms](https://ai.google.dev/gemma/terms) |
| OpenAI, Anthropic, Gemini APIs | Not allowed | Each forbids using outputs to build competing models | [OpenAI](https://openai.com/policies/row-terms-of-use/), [Bedrock terms](https://aws.amazon.com/legal/bedrock/third-party-models/), [Gemini](https://ai.google.dev/gemini-api/terms-archive/terms_05_02_24) |

The teacher protocol follows six findings:

- **Ask one yes/no question per option, and permute the option order.** This avoids the one-label-at-a-time suppression of listed answers ([Ma et al., search](https://aclanthology.org/2025.emnlp-main.126/)) and the position bias of option IDs ([PriDe, search](https://arxiv.org/abs/2309.03882)).
- **Combine teachers as annotators.** Use CROWDLAB-style weighting or a simple mean. Keep the soft set distribution where teachers disagree, and drop strong disagreements ([CROWDLAB](https://cleanlab.ai/blog/learn/multiannotator/)).
- **Expect inherited errors.** Students inherit non-random teacher errors, which entropy filters and ensembles fix only in part ([Lu & Smith 2025, search](https://arxiv.org/abs/2504.15432)).
- **Keep teacher tasks objective.** Teacher-made data hurts most on subjective tasks ([Li et al. 2023, search](https://aclanthology.org/2023.emnlp-main.647/)).
- **Avoid prompts tuned for recall.** One study saw 0.45 precision at 0.92 recall with such prompts ([search](https://pmc.ncbi.nlm.nih.gov/articles/PMC12481989/)).
- **Spot-check without showing teacher answers.** Human reviewers who see LLM suggestions drift towards them ([search](https://aclanthology.org/2025.findings-acl.1323.pdf)).

Existing open synthetic corpora help mostly as text and task seeds, not as gold:

- MoritzLaurer's synthetic_zeroshot_mixtral_v0.1 is Apache-2.0 and was made with Mixtral from 500+ tasks. It has about 2.63M rows, but whether a text carries several true labels is unverified ([dataset, search](https://huggingface.co/datasets/MoritzLaurer/synthetic_zeroshot_mixtral_v0.1)).
- Essential-Web's ODC-BY labels allow at most two labels per field ([paper, search](https://arxiv.org/abs/2506.14111)).

## Facts to re-check before any row is used

Huggingface.co, arXiv and the ACL Anthology were blocked during the research. No Hugging Face revision could be pinned for any dataset. Each fact below rests on weaker evidence than a primary page and must be re-checked.

| Fact used in this report | Current evidence | Re-check at |
|---|---|---|
| SQuAD 2.0 data is CC BY-SA 4.0 | Memory; only the repo's MIT LICENSE was read | SQuAD site and HF card |
| Natural Questions is CC BY-SA 3.0 | Archived HF card and search; MTEB says CC BY-NC-SA 3.0 | Google NQ download page |
| Natural Questions has about 51% "none" and about 8.4k-token pages | Secondary papers via search | Count on the train file |
| Qasper is CC BY 4.0 | Archived HF card (tag 2.0.0) and search | Current HF card |
| HUPD is CC BY 4.0 | GitHub README; one hint says the HF card shows CC BY-SA 4.0 | HF card |
| The MAVEN MIT licence covers the data files | The LICENSE is in the repo; the data is hosted off GitHub | Ask the authors (only matters under the loose rule) |
| DBpedia abstracts are CC BY-SA; CMU Movie Summary's CC BY-SA version | Knowledge; version unstated | DBpedia and CMU pages |
| Stack Exchange dumps up to April 2024 carry no LLM clause | DevClass article, not first-hand | archive.org dump terms |
| MuSiQue has 20 paragraphs per question and 19,938 train items | Search extract of an HF mirror | Data files |
| OpenAlex topic accuracy is 0.53 top-1 / 0.73 top-3; snapshots are now quarterly | Unpinned source; a blog post | OpenAlex docs |
| arXiv has about 150 categories and 1.5–2 per paper; Stack Exchange has 1–5 tags per question | Estimates | Count on the data |
| QAMPARI's gold completeness, and the false-negative rate of sampled distractors for all sources | Not measured | 200-item teacher check per source |
| Re-DocRED has 10–25 relation types per document; MAVEN 10–20 event types per document | Estimates | Count on the data |
| Qasper p90 length is 7.2k or 9.1k tokens | Two estimators disagree | Eos tokenizer |
| SATA d2 comes from RealToxicityPrompts with Perspective scores | My inference from the label set | SATA-Bench paper, Appendix A |
| SATA d6 source dataset; which MultiRC split d1 used | Not identified | SATA-Bench paper and HF card |
| SciFact, HoVer and Touché23 licences | Conflicting statements | Cards and authors |
| Aegis 2.0 and BRIGHTER are CC BY 4.0 | Third-party report; one HF commit | Live HF cards |
| xLAM-60k is CC BY 4.0, its generators, and its candidate counts | A mirrored card | Salesforce HF card (gated) |
| Qwen3 is Apache-2.0 for all models | Secondary source | Each Qwen3 model card |
| Gemma 4's licence and release date | Search extract; dates differ (31 March or 2 April) | Gemma model card |
| gpt-oss usage policy; Mixtral-8x22B and DeepSeek-V2 terms on outputs | Not read | Repos and licences |
| Mistral Large 3 is Apache-2.0 | A secondary wiki | Mistral licence page |
| Measuring Hate Speech target counts and "none" share | Not computed | Only if the loose rule is chosen |
| ESCI and WANDS annotation agreement | Not found | Papers and guidelines |
| Whether CC BY-SA share-alike reaches model weights | Legally unsettled | Counsel |

## Conclusion

E02 showed that a count head will learn whatever count distribution it is fed. The fix is therefore not more rows of the same kind, but a sampler that gives every source several count regimes, empty lists included, and a family list wide enough that no single family sets the prior. The SATA inspection changes what "unseen" means for this project. Half of SATA is document subject tagging, and E02 already trained on DBpedia-14 subject classes. So the boundary between "same family" and "same task type, new label set" decides what any zero-shot claim is worth. That boundary should be written down before E03 trains, and the planned with-and-without ablation should test it.

The binding limits are licences and family count, not volume. Four emails could turn the densest unclear sets into training data that the strict rule allows: QUEST, Ultra-Fine Entity Typing, SemEval ABSA, and the persuasion-technique sets after a news-overlap check. Beyond those, new families can only come from open-teacher data. That is where E03 and E04 should spend effort once the 80,000-row mix shows whether count transfer improves on the held-out tracks, measured per count bucket and per share of options correct.
