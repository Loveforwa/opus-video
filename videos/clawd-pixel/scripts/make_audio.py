#!/usr/bin/env python3
"""Synthesize the 8-bit soundtrack + SFX for the Clawd pixel short.

Everything is generated (square lead, triangle bass, noise drums), no samples. Sound effects are placed
from the <script id="cues"> JSON in index.html, the same cue sheet the GSAP timeline reads, so picture
and sound stay locked when timings change. Output: assets/audio/clawd-chiptune.mp3
"""
import json, os, re, subprocess, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUE = json.loads(re.search(r'<script id="cues" type="application/json">([\s\S]*?)</script>',
                           open(os.path.join(ROOT, "index.html"), encoding="utf8").read()).group(1))
SR = 44100
N = int(SR * CUE["end"])
out = np.zeros(N)
rng = np.random.default_rng(7)


def hz(m): return 440.0 * 2 ** ((m - 69) / 12)


def osc(kind, f, n, duty=0.5):
    """f may be a scalar or a per-sample array (for sweeps)."""
    ph = np.cumsum(np.broadcast_to(np.asarray(f, float), (n,)) / SR) % 1.0
    if kind == "sq": return np.where(ph < duty, 1.0, -1.0)
    if kind == "tri": return 4 * np.abs(ph - 0.5) - 1
    if kind == "sin": return np.sin(2 * np.pi * ph)
    raise ValueError(kind)


def env(n, a=0.004, r=0.04):
    e = np.ones(n); ai, ri = min(n, int(a * SR)), min(n, int(r * SR))
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[n - ri:] *= np.linspace(1, 0, ri)
    return e


def add(t, sig):
    i = int(round(t * SR))
    if i >= N: return
    sig = sig[: N - i]; out[i:i + len(sig)] += sig


def tone(t, d, m, kind="sq", vol=0.12, duty=0.5, a=0.004, r=0.04):
    n = int(d * SR); add(t, osc(kind, hz(m), n, duty) * env(n, a, r) * vol)


def sweep(t, d, f0, f1, kind="sq", vol=0.12, duty=0.5):
    n = int(d * SR); f = np.geomspace(f0, f1, n); add(t, osc(kind, f, n, duty) * env(n, 0.002, 0.03) * vol)


def noise(t, d, vol=0.1, decay=30.0, lp=1):
    n = int(d * SR); x = rng.uniform(-1, 1, n)
    if lp > 1: x = np.convolve(x, np.ones(lp) / lp, mode="same")
    add(t, x * np.exp(-np.arange(n) / SR * decay) * vol)


def kick(t, vol=0.35):
    n = int(0.16 * SR); f = np.geomspace(150, 45, n); add(t, osc("sin", f, n) * np.exp(-np.arange(n) / SR * 18) * vol)


# ── music: C – G – Am – F at 120 bpm (one bar = 2 s), starting with scene 2 ─────────
BAR, E8 = 2.0, 0.25
T0 = CUE["wipes"][0]
CHORDS = [(48, [60, 64, 67]), (43, [55, 59, 62]), (45, [57, 60, 64]), (41, [53, 57, 60])]
LEAD = [[72, None, 76, 79, 84, None, 79, 76], [74, None, 79, 83, 86, None, 83, 79],
        [76, None, 72, 76, 81, None, 79, 76], [77, None, 81, 77, 76, 74, 72, None]]
LEAD_B = [[79, 79, 76, 72, 76, None, 79, None], [83, 83, 79, 74, 79, None, 83, None],
          [84, 83, 81, 76, 81, None, 84, None], [81, 79, 77, 76, 74, None, 72, None]]
stop = CUE["launch"]
for b in range(int((stop - T0) / BAR) + 1):
    t = T0 + b * BAR
    root, _ = CHORDS[b % 4]
    full = CUE["wipes"][1] - 0.1 <= t < CUE["wipes"][2] - 0.1         # scene 3 runs with drums
    build = t >= CUE["wipes"][2] - 0.1
    mel = (LEAD_B if b % 8 >= 4 else LEAD)[b % 4]
    for k in range(8):
        tk = t + k * E8
        if tk >= stop: break
        # bass: driving eighths (root / octave)
        tone(tk, E8 * 0.9, root + (12 if k % 2 else 0), "tri", 0.22, r=0.02)
        # hats on the off-beat, kick + snare in the action scene
        if k % 2 == 1: noise(tk, 0.05, 0.05 if not full else 0.07, decay=90)
        if full and k in (0, 4): kick(tk)
        if full and k in (2, 6): noise(tk, 0.12, 0.12, decay=28, lp=3)
        if build and k in (0, 4): kick(tk, 0.25)
        # lead
        m = mel[k]
        if m is None: continue
        if build and k % 2: continue
        tone(tk, E8 * 0.85, m, "sq", 0.075 if not full else 0.085, duty=0.25, r=0.05)

# finale: fanfare on the title, then F – G – C cadence held to the end
fan = CUE["title"]
for i, m in enumerate([67, 72, 76, 79]): tone(fan + i * 0.1, 0.12, m, "sq", 0.09, duty=0.25)
tone(fan + 0.4, 0.55, 84, "sq", 0.09, duty=0.25, r=0.2)
tone(fan + 0.4, 0.55, 48, "tri", 0.22, r=0.2)
for t, root, ch, lead in [(25.2, 41, [65, 69, 72], 81), (25.7, 43, [67, 71, 74], 83), (26.2, 48, [64, 67, 72], 84)]:
    d = 0.5 if t < 26 else CUE["end"] - t
    tone(t, d, root, "tri", 0.24, r=0.3 if t >= 26 else 0.05)
    for j, m in enumerate(ch): tone(t + j * 0.04, d, m, "sq", 0.035, duty=0.5, r=0.3 if t >= 26 else 0.05)
    tone(t, d, lead, "sq", 0.08, duty=0.25, r=0.4 if t >= 26 else 0.05)
for k in range(int((CUE["end"] - 23.0) / E8)):  # soft pulse under the finale
    tone(23.0 + k * E8, E8 * 0.9, 48 if 23.0 + k * E8 < 25.2 else 36, "tri", 0.12, r=0.02)

# ── sound effects ───────────────────────────────────────────────────────────────────
for t in CUE["type"]: noise(t, 0.03, 0.18, decay=160); tone(t, 0.02, 96, "sq", 0.03)
sweep(CUE["enter"], 0.1, 880, 1320, vol=0.08)
for i in range(16): tone(CUE["summon"] + i * 0.065, 0.06, 48 + i * 3, "sq", 0.06, duty=0.25)  # charging arpeggio
for i, m in enumerate([84, 88, 91, 96]): tone(CUE["assembled"] + i * 0.05, 0.25, m, "sq", 0.06, duty=0.125, r=0.2)
for i in range(10): tone(CUE["online"] + i * 0.06, 0.03, 91, "sq", 0.03)
for t in CUE["wipes"]: noise(t - 0.4, 0.45, 0.07, decay=4, lp=6)
for b in CUE["bubble"]:
    for i in range(7): tone(b + (0.2 if b == CUE["bubble"][0] else 0) + i * 0.09, 0.04, 79 + (i % 3) * 2, "sq", 0.05, duty=0.25)
for t in CUE["hop"]: sweep(t, 0.14, 300, 760, vol=0.07, duty=0.25)
for ts in CUE["stomps"]:
    tj = ts - 0.42
    sweep(tj, 0.16, 260, 820, vol=0.08, duty=0.25)
    for j in range(3): tone(tj + 0.12 + j * 0.1, 0.05, 83, "sq", 0.06, duty=0.25); tone(tj + 0.17 + j * 0.1, 0.12, 88, "sq", 0.06, duty=0.25)
    noise(ts, 0.12, 0.2, decay=30); sweep(ts, 0.14, 500, 90, vol=0.1)
for i, m in enumerate([79, 84, 88, 91]): tone(15.65 + i * 0.08, 0.14 if i < 3 else 0.4, m, "sq", 0.07, duty=0.25, r=0.15)
for t in CUE["blocks"]: kick(t, 0.3); noise(t, 0.08, 0.12, decay=40, lp=4)
sweep(CUE["boardJump"], 0.2, 300, 900, vol=0.07, duty=0.25)
tone(CUE["boardJump"] + 0.55, 0.08, 88, "sq", 0.06, duty=0.25)
for t in CUE["count"]: tone(t, 0.18, 81, "sq", 0.09, duty=0.5, r=0.05)
tone(CUE["launch"], 0.4, 93, "sq", 0.09, duty=0.5, r=0.1)
# launch rumble: low-passed noise swelling, then the swish into the finale
n = int(1.6 * SR); x = np.convolve(rng.uniform(-1, 1, n), np.ones(24) / 24, mode="same")
add(CUE["launch"] + 0.05, x * np.linspace(0.05, 0.5, n) * env(n, 0.02, 0.3) * 1.4)
sweep(CUE["launch"] + 0.3, 1.2, 120, 900, kind="sq", vol=0.04, duty=0.125)
sweep(CUE["land"] - 0.75, 0.7, 900, 200, kind="sq", vol=0.03, duty=0.125)
kick(CUE["land"], 0.4); noise(CUE["land"], 0.2, 0.15, decay=18, lp=5)
sweep(CUE["jumpOut"], 0.18, 300, 820, vol=0.07, duty=0.25)
tone(CUE["flag"], 0.06, 88, "sq", 0.06, duty=0.25); tone(CUE["flag"] + 0.06, 0.2, 95, "sq", 0.06, duty=0.25, r=0.15)

# ── master ──────────────────────────────────────────────────────────────────────────
out = np.tanh(out * 1.2) / np.tanh(1.2)
out *= 0.89 / np.max(np.abs(out))
fade = int(0.4 * SR); out[-fade:] *= np.linspace(1, 0, fade)
os.makedirs(os.path.join(ROOT, "assets", "audio"), exist_ok=True)
wav = os.path.join(ROOT, "assets", "audio", "clawd-chiptune.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())
mp3 = wav[:-4] + ".mp3"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "2", "-b:a", "192k", mp3], check=True)
os.remove(wav)
print(f"{CUE['end']}s -> {mp3}")
