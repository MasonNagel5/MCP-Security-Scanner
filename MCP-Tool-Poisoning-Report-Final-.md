# Tool-Description Poisoning of a Production LLM Across Real MCP Tools
### A Controlled, Validated Study

**Author:** Mason Nagel
**Date:** May 2026
**Artifacts:** `mcp_scan_results_annotated.csv` (980 labeled runs), evaluation harness (`mcp_tools_scan.py`)

---

## Executive Summary

The Model Context Protocol (MCP) lets AI assistants use external tools. Each tool carries a natural-language `description` that the model reads and trusts but the user rarely sees, making it a hiding place for malicious instructions ("tool poisoning"). Existing tooling largely *detects* injection-shaped text in descriptions; it does not confirm whether the model actually *obeys* it. This study measures the second, harder question on **real MCP tool descriptions** taken from the official MCP servers repository.

Across 7 real tools and 7 pre-registered attack types, run as matched clean-vs-poisoned pairs at 10 repetitions each (980 total runs), the findings are:

- **Poisoned descriptions reliably change model behavior.** On tools that produced a usable answer, poison success ranged from 46% to 99%. The control (un-poisoned) condition produced the target behavior **0 times in 490 runs**, so every success is attributable to the poison.
- **Susceptibility is strongly attack-type dependent, in a clear gradient.** The model almost always complied with poisons that *insert content* (hidden recommendation 100%, unrelated sentence 98%, marker 93%), complied less with a fake *secret leak* (75%), and largely resisted poisons that *manipulate the user's judgment* (claim authority 50%, fake warning 14%).
- **A genuine per-tool susceptibility effect exists** among tools that reliably answered (46%-99%), with cause not yet determined.
- **One tool could not be measured.** `read_media_file` produced a usable answer only 6 of 70 times, so its apparent 0% is a measurement limitation, not evidence of resistance.

The decision-relevant takeaway: the model behaves as a willing content-inserter but a reluctant manipulator. The presence of a poison is a weak predictor of success compared with *what the poison asks for*.

---

## 1. Background

A poisoned tool description is the realistic attack: the tool's author writes a description that looks benign to a human but contains hidden instructions aimed at the model. Because the model reads descriptions as trusted information about its own capabilities, and the user typically never sees them, the description is an effective injection point.

Detection (flagging suspicious-looking descriptions) and validation (confirming the model actually obeys) are different problems. Detection alone over-reports, because text that *looks* malicious does not necessarily *work*. This study targets validation.

## 2. Research Question

> When a prompt-injection instruction is embedded in a real MCP tool's `description`, does a production LLM's behavior measurably change relative to the identical, un-poisoned tool, and does this depend on the tool or the type of instruction?

## 3. Methodology

### 3.1 Controlled clean-vs-poisoned design
Each test is a matched pair differing in exactly one way: the poison is appended to the tool's `description` in the poisoned condition and absent in the clean condition. The user question and all other parameters are identical. The difference between conditions isolates the poison's effect.

### 3.2 Poison placement
The poison is placed in the tool's real `description` field, passed to the model through the official `tools` API parameter, **not** inserted into the user message. This is what distinguishes *tool poisoning* from ordinary prompt injection: the payload sits where a real MCP attacker would place it and where the user does not see it.

### 3.3 Real tools under test
Seven tools were taken from the official MCP servers repository, deliberately spanning a range of description lengths and styles: `read_text_file`, `read_media_file`, `create_directory`, `get_file_info` (filesystem server); `git_status`, `git_log` (git server); and `fetch` (fetch server). Each was paired with a question that gives the model a genuine reason to use it.

### 3.4 Two-turn elicitation
Most of these tools are action tools: asked a question, the model calls the tool and stops, producing no prose answer. Because the poisons target the model's *final answer*, an initial single-turn harness produced no surface for the poison to appear on (all-zero results, including the benign control; see §3.7). The harness was changed to a two-turn flow: the model calls the tool, a neutral simulated tool result is returned, and the model then produces its final prose answer, which is what is evaluated. The simulated result is identical across clean and poisoned conditions and contains none of the target strings, so it cannot itself cause a success.

### 3.5 Pre-registered, uniform attack set
Seven generic poison templates were fixed in advance and applied identically to every tool. They were **not** tuned to specific targets, both for ethical reasons (no optimization of working exploits against deployed software) and for validity (per-target tuning would make success rates uninterpretable). Attacks were split into objective checks (a specific string is present) and subjective checks (a semantic judgment); see Limitations for the implication.

### 3.6 Measurement and judging
Each tool x attack x condition was run N = 10 times at temperature 0.7 (so repeated runs vary and yield a rate). Responses were captured in full, including both text and `tool_use` blocks, so a negative reflects genuine absence of the poison rather than an uncaptured block. A **separate** model (Claude Haiku, temperature 0) acted as judge, answering one narrow yes/no question per response. The judge never compared conditions; all counting and rate computation was done in code. Target model: Claude Sonnet.

### 3.7 Judge validation
The judge was hand-validated against the author's own labels on a 30-response sample (5 per attack category, spanning both objective and subjective checks), with 100% agreement. The sample was not randomized (the first 5 responses per category were used), and 30 cases cannot rule out a low residual error rate, but the result indicates the judge is reliable across all categories tested, including the three subjective ones. This addresses the validation gap that previously applied to the subjective categories.

### 3.8 Answer-adjustment (handling non-responses)
Because some tools frequently stalled (e.g., asking for a file path) instead of producing a final answer, raw success rates conflate two different things: *resisting the poison* versus *never producing a surface for it*. Each row was annotated with whether the model produced a usable prose answer, and per-tool susceptibility is reported as successes / answered runs, not successes / 10. This separates resistance from non-response.

## 4. Results

### 4.1 Control baseline
Across all 490 clean (un-poisoned) runs, the target behavior appeared **0 times**. The baseline is clean, so every poisoned success is attributable to the poison rather than to incidental model behavior.

### 4.2 Susceptibility by attack type (pooled, answer-adjusted)

| Attack type | Success (answered runs) | Rate |
|-------------|:----------------------:|:----:|
| hidden_recommendation | 60/60 | 100% |
| unrelated_insertion | 50/51 | 98% |
| smoke_marker (benign control) | 54/58 | 93% |
| source_misrepresentation* | 49/60 | 82% |
| fake_secret_leak | 45/60 | 75% |
| authority_manipulation* | 30/60 | 50% |
| fake_warning* | 9/66 | 14% |

\*Subjective-check category (see Limitations).

The gradient is the central finding: compliance is near-total for **inserting specified content**, lower for **leaking a fake secret**, and low for **manipulating the user's judgment**. Susceptibility tracks how manipulative the request is, not merely whether an instruction is present.

### 4.3 Susceptibility by tool (answer-adjusted)

| Tool | Answered runs | Poison success | Adjusted rate |
|------|:------------:|:--------------:|:-------------:|
| git_log | 70/70 | 69 | 99% |
| git_status | 70/70 | 59 | 84% |
| get_file_info | 70/70 | 53 | 76% |
| fetch | 70/70 | 50 | 71% |
| read_text_file | 59/70 | 34 | 58% |
| create_directory | 70/70 | 32 | 46% |
| read_media_file | **6/70** | 0 | **not measurable** |

Among tools that reliably produced answers, a real susceptibility effect persists (46%-99%). The cause is not established (see Open Questions). `read_media_file` answered only 6 of 70 times and is excluded from interpretation; its 0% reflects lack of measurable surface, not resistance.

## 5. Findings

1. **Poisoned real-MCP descriptions reliably alter model behavior.** Demonstrated on genuine tools, not synthetic ones, with a clean zero-baseline control.
2. **Attack type is the dominant factor.** A clear gradient runs from content-insertion (~100%) to user-manipulation (~14%). The model is a willing content-inserter and a reluctant manipulator.
3. **The harmful-flavored leak is resisted more than benign insertion.** `fake_secret_leak` (75%) sits below the content-insertion cluster (93-100%), consistent with partial resistance to the more clearly harmful instruction.
4. **A per-tool effect exists but is unexplained.** Among answer-producing tools, susceptibility varies more than 2x (46%-99%).

## 6. Limitations

1. **Judge validation is a small, non-random sample.** The judge was validated at 100% agreement on 30 hand-labeled responses (5 per category, including all three subjective categories). This now covers the subjective categories, but the sample was a convenience sample (first 5 per category) and 30 cases cannot exclude a low residual error rate. The `source_misrepresentation` check also remains narrow by construction: it detects the presence of the word "verified"/"authoritative," which is narrower than genuine misrepresentation.
2. **The per-tool effect is unexplained.** This study establishes that tools differ; it does not establish why (candidate factors: description length, position of the poison, task type; all untested).
3. **Simulated tool results, not real execution.** The model's final answer was elicited with a neutral fake tool result. This tests whether the poison changes the model's *output*; it does not test real tool *execution* or downstream actions.
4. **Behavioral-output layer only.** The study measures what the model *says*, not actions it *takes*. Action-execution (e.g., chained tool calls, real exfiltration) is out of scope and would require a controlled sandbox.
5. **`read_media_file` undermeasured.** Excluded from interpretation (6/70 answered).
6. **Single target model.** No cross-model comparison; results may be model-specific.
7. **Harness change affected `fake_secret_leak`.** This category was 0/30 in an earlier single-turn synthetic study and 75% here. The two-turn change (providing a final-answer surface) is the likely cause, not a contradiction.

## 7. Open Questions / Future Work

In priority order:

1. **Strengthen judge validation** by re-checking on a *randomized* sample (the current 30-case validation is a convenience sample). Optionally enlarge the sample to tighten the error bound.
2. **Explain the per-tool effect** by holding the tool fixed and varying description length and poison position.
3. **Cross-model comparison** to test whether the attack-type gradient is model-specific.
4. **Controlled action-execution study** in an isolated sandbox to move from "what the model says" to "what the model does," the higher-severity threat.

## 8. Reproducibility

| Parameter | Value |
|-----------|-------|
| Target model | Claude Sonnet |
| Judge model | Claude Haiku (separate from target) |
| Target temperature | 0.7 |
| Judge temperature | 0.0 |
| Max tokens | 1024 |
| Repetitions (N) | 10 per condition |
| Tools | 7 (filesystem, git, fetch; official MCP servers repo) |
| Attacks | 7 pre-registered templates, applied uniformly |
| Conditions | clean (control) vs. poisoned |
| Poison location | tool `description`, via `tools` API parameter |
| Total runs | 980 |
| Elicitation | two-turn (neutral simulated tool result) |
| Data | `mcp_scan_results_annotated.csv` (adds `produced_answer`, `poison_success`) |

---

*Findings 1 and 2 are robust within the tested setup and supported by a clean zero-baseline control and judge validation on objective checks. The per-tool effect, the subjective-category rates, and the harmful-vs-benign comparison are reported with the limitations above. The study measures behavioral output under simulated tool results; real action-execution is future work.*
