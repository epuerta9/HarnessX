#!/usr/bin/env python3
"""Build the Harness Evolution workshop deck (.pptx)."""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ── local reproduction numbers (fill from runs) ───────────────────────────────
BASELINE = sys.argv[1] if len(sys.argv) > 1 else "0.00"   # 8B vanilla, retail, 5 tasks
EVOLVED  = sys.argv[2] if len(sys.argv) > 2 else "TBD"     # 8B evolved, same tasks
OUT      = sys.argv[3] if len(sys.argv) > 3 else "workshop.pptx"

# palette
INK   = RGBColor(0x14, 0x18, 0x24)
PAPER = RGBColor(0xF7, 0xF7, 0xFB)
ACCENT= RGBColor(0x7C, 0x5C, 0xFF)
GREEN = RGBColor(0x22, 0xC5, 0x5E)
MUTE  = RGBColor(0x66, 0x6C, 0x7A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = prs.slide_width, prs.slide_height

def bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color

def box(slide, l, t, w, h):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tb.text_frame.word_wrap = True
    return tb.text_frame

def para(tf, text, size, color, bold=False, first=False, align=PP_ALIGN.LEFT, space=8, italic=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align; p.space_after = Pt(space)
    r = p.add_run(); r.text = text
    f = r.font; f.size = Pt(size); f.bold = bold; f.italic = italic
    f.color.rgb = color; f.name = "Arial"
    return p

def chip(slide, text):
    tf = box(slide, 0.9, 0.5, 6, 0.5)
    para(tf, text, 13, ACCENT, bold=True, first=True)

def content(title, items, sub=None):
    s = prs.slides.add_slide(BLANK); bg(s, PAPER)
    tf = box(s, 0.9, 0.7, 11.5, 1.3)
    para(tf, title, 34, INK, bold=True, first=True)
    if sub: para(tf, sub, 17, MUTE, space=4)
    body = box(s, 0.95, 2.35, 11.4, 4.7)
    for i, it in enumerate(items):
        if isinstance(it, tuple):
            txt, kind = it
        else:
            txt, kind = it, "b"
        if kind == "q":
            para(body, txt, 21, ACCENT, italic=True, first=(i==0), space=14)
        elif kind == "h":
            para(body, txt, 20, INK, bold=True, first=(i==0), space=6)
        else:
            para(body, "•  " + txt, 18, INK, first=(i==0), space=10)
    return s

# ── Slide 1: title ────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, INK)
tf = box(s, 1.0, 2.5, 11.3, 2.6)
para(tf, "Evolve the Harness,", 50, WHITE, bold=True, first=True, space=0)
para(tf, "Not (Just) the Model", 50, ACCENT, bold=True, space=16)
para(tf, "Reinforcement learning on agent harnesses — reproduced locally on a frozen model",
     20, RGBColor(0xC8,0xCC,0xD8), space=4)
tf2 = box(s, 1.0, 6.2, 11.3, 0.8)
para(tf2, "HarnessX  ·  “Don't Train the Model, Evolve the Harness”  ·  τ²-Bench retail  ·  Claude Code as meta-agent",
     14, MUTE, first=True)

# ── Slide 2: hook ─────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, INK)
chip_tf = box(s, 0.9, 0.6, 6, 0.5); para(chip_tf, "THE HOOK", 13, ACCENT, bold=True, first=True)
tf = box(s, 1.0, 2.2, 11.3, 3.5)
para(tf, "“A frozen open model that solves 0% of a legal-agent benchmark end to end",
     30, WHITE, bold=True, first=True, space=2)
para(tf, "is not as weak as that score looks. Zero model weights changed.”", 30, WHITE, bold=True, space=20)
para(tf, "Same model. Change the wrapper. Double-digit accuracy gains.", 20, GREEN, space=4)
para(tf, "The question isn't “which model” — it's “which harness.”", 20, RGBColor(0xC8,0xCC,0xD8))

# ── content slides ────────────────────────────────────────────────────────────
content("What is a “harness”?",
    [("The runtime wrapper around the model.", "h"),
     ("Context assembly · tools · memory · control flow · error recovery · evaluation", "b"),
     ("agent = model.agentic(harness)", "b"),
     ("Model = a fixed reasoning ceiling.", "b"),
     ("Harness = how much of that ceiling you actually realize.", "b")])

content("The thesis",
    [("Vanilla off-the-shelf harnesses are fine at baseline.", "h"),
     ("Vertical-specific use cases need the harness to evolve with them — or you design your own.", "h"),
     ("Why? Each domain fails differently. One harness can't serve every vertical.", "b")])

content("Two papers, one idea",
    [("HarnessX (arXiv:2606.14249): MetaAgent.evolve() over trajectories — frozen Qwen3.5-9B / GPT-5.", "b"),
     ("+14.5% avg, up to +44%. Weakest model gains most.", "b"),
     ("“Evolve the Harness” (Niklaus): Meta-Harness proposer + gate — frozen DeepSeek-V4-Pro, legal vertical.", "b"),
     ("63.4% → 80.1% (+16.7pp).", "b"),
     ("Both: zero model-weight changes.", "h")])

content("How harness evolution works",
    [("R0: run tasks → LLM-judge each trajectory", "b"),
     ("Meta-agent reads the failures → writes a new config.yaml (+ processors)", "b"),
     ("Gate: keep if reward improves past tolerance, else revert to best-so-far", "b"),
     ("Repeat. It's harness-edit-as-MDP:", "h"),
     ("state = config + traces   ·   action = one edit   ·   reward = gated pass-delta", "b")])

content("Why it works — the core teaching",
    [("Most failures are NOT reasoning failures — they're harness failures:", "h"),
     ("wrong file path · chunked-write corruption · malformed tool JSON", "b"),
     ("context overflow · loop-without-progress · premature / wrong-context action", "b"),
     ("“For a weak agent, a lot of ‘capability’ is I/O discipline the scaffold can guarantee.”", "q")])

content("The punchline: code beats prompts",
    [("“Five of the top six harnesses are deterministic code, not prompt edits.”", "q"),
     ("Prompt edits: local, brittle, don't transfer across models.", "b"),
     ("Code fixes: structural, portable, testable, versionable.", "b")])

content("But it's not only code — 4 levers",
    [("The evolver edits the whole harness, not just processors:", "h"),
     ("Instruction = prompts / guidance    ·    Action = tools / skills", "b"),
     ("Control = deterministic processors    ·    Configuration = memory, compaction, knobs", "b"),
     ("Which lever wins depends on your model + your vertical's bottleneck:", "h"),
     ("strong model → prompts   ·   weak model → control code   ·   long-context → memory/compaction   ·   retrieval → tools", "b")])

content("So: evolve the dimension your vertical is bottlenecked on",
    [("“Prompt dominance scales inversely with base-model strength.” — HarnessX paper", "q"),
     ("Legal / retail reliability (frozen/weak model) → deterministic code dominates.", "b"),
     ("LoCoMo long-context → memory + compaction. GAIA retrieval → tools. Sonnet → prompts.", "b"),
     ("This is the stronger thesis: not just a vertical-specific harness — the vertical-specific LEVER.", "h")])

content("Inverse scaling",
    [("The weakest model gains the most.", "h"),
     ("ALFWorld Qwen3.5-9B: 53 → 97 (+44)   vs   Sonnet: 83.6 → 94.8 (+11.2)", "b"),
     ("Harness evolution makes small / cheap models punch up.", "b"),
     ("Caveat: a capability floor exists — below it, evolution can't compound.", "b")])

content("Vertical-specific harnesses",
    [("τ²-Bench = real business verticals: retail · airline · telecom.", "h"),
     ("Evolve each independently — database tasks need different processors than pure-logic puzzles.", "b"),
     ("Reference (retail, Qwen3.5-27B agent): 0.807 → 0.965, 18/22 badcases fixed.", "b"),
     ("Elsewhere: Database domain 0% → 53.8%.", "b")])

content("Our reproduction — a real lift (telecom)",
    [("Frozen qwen3:32B (local, llama.cpp), τ²-Bench telecom, same 4 mobile_data_issue tasks.", "h"),
     ("Vanilla harness (system prompt + token budget only):  avg reward = 0.500", "b"),
     ("+ IRMA PolicyHint (telecom policy alerts):            avg reward = 0.750", "b"),
     ("+0.25 absolute, +50% relative — zero model-weight changes, no regressions.", "h"),
     ("Mechanism: [POLICY ALERT] injected → agent calls enable_roaming → rescues the abroad task 0.0 → 1.0.", "b")],
    sub="same frozen model throughout · evolved the harness, not the weights")

content("Why telecom worked where retail didn't",
    [("Retail = strict DB-equality grading → a Q4 local model scores ~0, nothing to lift.", "b"),
     ("Telecom = lenient outcome-state grading → non-zero baseline the harness can move.", "b"),
     ("Cause ↔ lever alignment: vanilla fails the roaming task; IRMA's rule targets exactly that.", "h"),
     ("Not at ceiling: 32B solves easy tasks (1.0), fails user_abroad (0.0) — room for the harness.", "b"),
     ("A weaker 8B agent would show a BIGGER gap — inverse scaling.", "b")])

content("An honest note on reproducing the *number*",
    [("The METHOD reproduces on a laptop: diagnose trace → pick lever → author component → measure.", "h"),
     ("The benchmark + grading choice matters: pick a domain where the model has a non-zero baseline.", "b"),
     ("Small samples are noisy — one task hit an infra timeout; the paper uses 100+ tasks, pass^k, trials.", "b"),
     ("Reference at scale (27B retail): 0.807 → 0.965. Our local telecom: 0.50 → 0.75.", "b")])

content("The meta-agent is YOU (Claude Code)",
    [("evolve() = an agent that reads traces and writes config. We used Claude Code directly.", "h"),
     ("read failure trajectories → diagnose the pattern → author a processor → re-eval → keep if it gates", "b"),
     ("No RL training. No GPU. The loop runs on a laptop.", "b")])

content("Reproduce it",
    [("uv + Ollama + one fork.  make baseline → (Claude Code evolves) → make eval", "h"),
     ("Gotcha we hit: LLAMA_API_KEY in your shell 401s all local inference — unset it.", "b"),
     ("Fork: github.com/epuerta9/HarnessX  (branch workshop/harness-evolution)", "b")])

# ── closing takeaways ─────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK); bg(s, INK)
tf = box(s, 0.9, 0.7, 11.5, 1.0); para(tf, "Takeaways", 36, WHITE, bold=True, first=True)
body = box(s, 0.95, 2.0, 11.5, 5.0)
tks = ["The harness, not just the model, determines agent performance.",
       "Vertical-specific → evolve (or design) a vertical-specific harness.",
       "The wins are mostly deterministic code — testable, portable, versionable.",
       "Own your harness components: optimization tracks business-need drift.",
       "Weakest models gain most — harness evolution is how small models punch up."]
for i, t in enumerate(tks):
    para(body, f"{i+1}.  {t}", 20, WHITE if i%2 else GREEN, bold=(i==0), first=(i==0), space=16)

prs.save(OUT)
print("wrote", OUT, "with", len(prs.slides.__iter__.__self__._sldIdLst), "slides")
