# Alternatives considered

Every approach we discussed that serves the same goal, with where it stands. "Yours" = from the original project
write-up; "others" = existing systems; "ours" = proposed during planning.

| Approach | Origin | Zero-shot on new labels | Set probabilities | Captures "B implies A" | Cost | Status |
|---|---|---|---|---|---|---|
| One yes/no (Noul) per option | others (Jev workaround, LLEV `multi`, Decision Index) | yes | assumes independence | no | K questions | **Baseline** |
| Yes/no + tuned thresholds / Platt | others ([2609.37647](https://arxiv.org/abs/2609.37647)) | no (needs labels per task) | same | no | trivial | **Baseline** |
| Post-hoc CRF / Ising over probabilities | yours (direction 1) | no (needs labels per task) | yes | yes | low | Parked: add-on for repeated tasks |
| One sigmoid per option, options in view | yours (direction 2); GLiClass, JevK5-Lite | yes | product, implicit count | no | low | **Main ablation** |
| **Per-option scores + count head** | ours | yes | yes, explicit count | only via count | +~40k params | **Primary** |
| Chain head over options (classifier chain) | yours (direction 3) | yes | full joint | yes | sequential, order-sensitive | Escalation if E02/E03 show residual dependence |
| Linked question groups (relaxed isolation) | yours (direction 4) | yes | yes | yes | needs attention-only backbone | Parked (see below) |
| Subsets as Choice options (`set_choice`-style) | others (Haste Jev) | yes | yes | yes | exponential in K | Only for tiny K |
| LLM writes a list | others | yes | poor | yes | slow | Comparison only |
| Discrete diffusion over answer slots | your seeds | — | one denoising step is factorised | only multi-step | high | Dropped |
| Conformal answer sets | your seeds | needs calibration data per task | coverage guarantee | — | low | Optional wrapper later |
| Coherence projection across questions | ours | yes | — | — | trivial | Parked with linked groups |

## Why the parked ones are parked

- **Linked question groups.** "Relax the attention mask" does not work on hybrid backbones (Qwen3.5/3.8 Gated
  DeltaNet layers ignore masks; every current Kev runs each question as its own row), and packing linked questions in
  sequence makes answers order-dependent. A cheap competitor exists: ask Q1, write its answer into the state, ask Q2
  (the cached state makes the second call nearly free). And measured incoherence is small on average: Jev's
  "X" / "not X" probabilities miss summing to 1 by 0.064 on average ([2609.33209](https://arxiv.org/abs/2609.33209)).
  If revisited, start with projecting a declared group's answers onto the coherent set, which provably lowers the
  Brier score (Predd et al. 2009), before any model change. If a learned version is needed, do it as late interaction:
  a tiny head over per-question readout vectors, which keeps backbone isolation intact.
- **Diffusion.** One parallel denoising step predicts each masked slot independently given the context, i.e.
  independent marginals. Dependence only enters through multi-step unmasking, which is a chain in a learned order.
- **Conformal.** Its guarantees need exchangeable calibration data for each task; runtime-defined labels usually have
  none. Useful later as a wrapper for repeated tasks.
- **Post-hoc CRF.** Needs labelled data per task, so it cannot be the zero-shot primitive. Useful later as an add-on.

## When the chain head comes back

Only if, after training the count model (E03), a clear gap remains on real data between the count model and
something that models pairwise dependence (e.g. pairwise terms fitted on dev residuals), while synthetic data with
built-in dependence confirms the measurement can detect it.
