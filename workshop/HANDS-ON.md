# Hands-On Lab — Feel the Baseline, Then Evolve It Yourself

> This is not a copy-the-answer lab. You run a frozen model on a real benchmark, **watch it fail in the
> trace**, and let **your own Claude Code** evolve the harness using the HarnessX framework. The point is
> the *loop* — diagnose → pick a lever → author a fix → measure — not a specific patch.

You'll reproduce a real result on a laptop: **same frozen model, vanilla harness 0.50 → evolved 0.75**,
by discovering the fix yourself.

---

## 0. Setup (once)

```bash
git clone https://github.com/epuerta9/HarnessX && cd HarnessX
git clone https://github.com/sierra-research/tau2-bench ~/tau2-bench
cd workshop && make setup            # uv sync + install tau2-bench + pull qwen3 models
./serve-local.sh ollama              # local inference (unsets LLAMA_API_KEY; --jinja on)
cp .env.example ../.env              # routing: agent + user-sim → local
```
If you see `Invalid API Key` or 0.00 everywhere, read `README.md` § Troubleshooting (LLAMA_API_KEY / --jinja).

Give your Claude Code the evolver role once:
```bash
cp -r evolver-skill ~/.claude/skills/harness-evolver     # or reference it inline
```

---

## 1. Experience the baseline (feel it fail)

Run the **vanilla** harness on telecom — a real customer-support benchmark:
```bash
make baseline DOMAIN=telecom TASKS=6
```
Watch the tasks run. Some pass, some **fail**. Note the avg reward. **This is the "before" you own.**

---

## 2. Read the trace — where does it hurt?

Open a failing trajectory and read the **frontmatter** (the diagnostic dashboard):
```bash
ls ../recipe/tau2_evolver/runs/baseline/R0/trajectories/
sed -n '1,30p' ../recipe/tau2_evolver/runs/baseline/R0/trajectories/*user_abroad*.md
```
Ask yourself (these are the fields that matter):
- `judge_cause` — *why* did it fail?
- `expected_actions` vs `executed_actions` — did it do the right things?
- `failed_actions` — *which* step is missing?
- `exit_reason` / `tool_error_counts` — how did it end; was it a reliability or strategy failure?

On telecom `user_abroad` tasks you'll typically see the agent never calls `enable_roaming` — a
**harness failure, not a reasoning failure**. Sit with that: the model *could* do it; the scaffold didn't
guide it there.

---

## 3. Evolve it — with YOUR Claude Code

In Claude Code, invoke the evolver skill on your baseline run:

> "Use the **harness-evolver** skill. Read `recipe/tau2_evolver/runs/baseline/R0/trajectories/`,
> diagnose the dominant failure, and author a HarnessConfig (+ any processor) that fixes it. Explain
> which of the 4 levers you chose and why."

Your Claude will (per the skill): sweep the frontmatter → cluster by `judge_cause` → map cause → **lens ×
lever × intent** → author a `config.yaml` (+ a `MultiHookProcessor` if it picks the Control lever) →
self-validate with `canonicalize()`. **You are the meta-agent; the model weights never change.**

The 4 levers it's choosing among:
| Lever | Component | When |
|-------|-----------|------|
| Instruction | prompt / guidance | strong model, subtle rule |
| Action | tools / skills | retrieval / capability gap |
| Control | deterministic processor | weak model, I/O discipline — **usually here** |
| Configuration | memory / compaction / knobs | long-context, retune |

---

## 4. Measure — did it lift?

```bash
make eval DOMAIN=telecom CONFIG=<path-to-your-config.yaml> TAG=myfix TASKS=6
```
Compare `runs/myfix/` vs `runs/baseline/`. Did the avg reward rise? Did the failing task flip? Did
anything **regress**? If it regressed, that's data — read the new trace and pull a different lever.

**Loop steps 2–4 until it improves.** That's harness evolution.

---

## 5. Compare with a reference solution (only after you've tried)

We shipped one worked answer for telecom — the framework's telecom IRMA processor:
`evolved/harness_config_telecom.yaml` (enables `PolicyHintProcessor`, whose `roaming_disabled_abroad`
rule injects a `[POLICY ALERT] → call enable_roaming`).
```bash
make eval DOMAIN=telecom CONFIG=evolved/harness_config_telecom.yaml TAG=telecom_irma TASKS=6
```
Reference result (qwen3:32B, 4 tasks): **0.50 → 0.75 (+50%)**, rescuing the `user_abroad` roaming task,
no regressions. Did your fix find the same lever? A different one? Both are valid if the number moved.

Full worked rationale: `evolved/EVOLVE-JOURNAL.md`. Method + trace-reading: the KB notes 02, 03, 07.

---

## What you should walk away having *felt*
1. A frozen model's realized score is mostly **I/O discipline the scaffold guarantees** — you saw it fail,
   then saw a harness edit (no weight change) fix it.
2. **You** drove the evolve loop with your own Claude — read trace, chose a lever, measured.
3. The lever depends on your **vertical's bottleneck** — which is why one vanilla harness can't serve
   every use case.
4. This is how you **squeeze a cheap/small model** to punch up on *your* problem.
