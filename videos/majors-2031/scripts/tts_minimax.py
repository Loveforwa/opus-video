#!/usr/bin/env python3
"""MiniMax TTS → per-frame voice files + audio_meta.json for the HyperFrames pipeline.

Usage:
  MINIMAX_API_KEY=... python3 scripts/tts_minimax.py lines   --voice <voice_id> [--speed 1.08]
  MINIMAX_API_KEY=... python3 scripts/tts_minimax.py audition --text "..." --voices a,b,c

`lines` reads SCRIPT.md, synthesizes one mp3 per `## Line N … (Frame N)` block into
assets/audio/vo/frame-NN.mp3 and writes audio_meta.json in the frame-keyed shape that
faceless-explainer's captions.mjs / assemble-index.mjs consume:
  { bgm, bgm_pending, voices: [{frame, path, duration_s, words:[{id,text,start,end}]}], sfx }
Word timings: MiniMax returns sentence-level subtitles; each sentence is split into
clauses at Chinese punctuation and clause times are distributed by character count.
The API key is read from the environment only — never written to disk by this script.
"""
import argparse, json, os, re, subprocess, sys, urllib.request

API = os.environ.get("MINIMAX_API_BASE", "https://api.minimaxi.com") + "/v1/t2a_v2"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def synth(text, voice, speed, out_path):
    key = os.environ["MINIMAX_API_KEY"]
    body = {
        "model": "speech-2.6-hd",
        "text": text,
        "stream": False,
        "language_boost": "Chinese",
        "voice_setting": {"voice_id": voice, "speed": speed, "vol": 1.0, "pitch": 0},
        "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1},
        "subtitle_enable": True,
    }
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.load(r)
    if d.get("base_resp", {}).get("status_code") != 0:
        raise SystemExit(f"MiniMax error: {d.get('base_resp')}")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(bytes.fromhex(d["data"]["audio"]))
    subs = []
    url = (d.get("data") or {}).get("subtitle_file")
    if url:
        with urllib.request.urlopen(url, timeout=60) as r:
            subs = json.load(r)
    return subs


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return round(float(out), 3)


CLAUSE = re.compile(r"[^，。：；！？、——…]+[，。：；！？、——…]*")


def words_from_subs(subs, text, total):
    """Sentence-level subtitles → clause-level 'words' with frame-relative seconds."""
    segs = []
    for s in subs or []:
        t = s.get("text", "")
        b = s.get("time_begin", 0) / 1000.0
        e = s.get("time_end", 0) / 1000.0
        if t.strip():
            segs.append((t, b, e))
    if not segs:  # fallback: whole line spans the clip
        segs = [(text, 0.0, total)]
    words = []
    for t, b, e in segs:
        clauses = [c.strip() for c in CLAUSE.findall(t) if c.strip()] or [t]
        n = sum(len(re.sub(r"\s", "", c)) for c in clauses) or 1
        cur = b
        for c in clauses:
            span = (e - b) * len(re.sub(r"\s", "", c)) / n
            shown = c.rstrip("，、：；——") or c  # keep sentence-final 。！？ for grouping
            words.append({"id": f"w{len(words)}", "text": shown, "start": round(cur, 3), "end": round(cur + span, 3)})
            cur += span
    return words


def parse_script(md):
    out, cur = [], None
    for line in md.splitlines():
        h = re.match(r"^#{2,3}\s+.*?\(frame\s+(\d+)\)", line, re.I)
        if h:
            if cur and cur["text"].strip():
                out.append(cur)
            cur = {"frame": int(h.group(1)), "text": ""}
            continue
        if not cur or line.lstrip().startswith("**"):
            continue
        m = re.match(r"^(?: {4,}|\t)(.+)$", line)
        if m:
            cur["text"] += m.group(1).strip()
    if cur and cur["text"].strip():
        out.append(cur)
    return out


def cmd_lines(a):
    lines = parse_script(open(os.path.join(ROOT, "SCRIPT.md"), encoding="utf8").read())
    only = {int(x) for x in a.only.split(",")} if a.only else None
    meta_path = os.path.join(ROOT, "audio_meta.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {"bgm": None, "bgm_pending": False, "voices": [], "sfx": []}
    byf = {v["frame"]: v for v in meta.get("voices", [])}
    for ln in lines:
        if only and ln["frame"] not in only:
            continue
        rel = f"assets/audio/vo/frame-{ln['frame']:02d}.mp3"
        subs = synth(ln["text"], a.voice, a.speed, os.path.join(ROOT, rel))
        dur = duration(os.path.join(ROOT, rel))
        byf[ln["frame"]] = {"frame": ln["frame"], "path": rel, "duration_s": dur,
                            "words": words_from_subs(subs, ln["text"], dur)}
        print(f"frame {ln['frame']:2d}  {dur:6.2f}s  {ln['text'][:28]}…")
    meta["voices"] = [byf[k] for k in sorted(byf)]
    json.dump(meta, open(meta_path, "w"), ensure_ascii=False, indent=2)
    print("total voice", round(sum(v["duration_s"] for v in meta["voices"]), 2), "s →", meta_path)


def cmd_audition(a):
    for v in a.voices.split(","):
        rel = f"assets/audio/audition/{re.sub(r'[^A-Za-z0-9_-]+', '_', v)}.mp3"
        synth(a.text, v, a.speed, os.path.join(ROOT, rel))
        print(f"{v:45s} {duration(os.path.join(ROOT, rel)):6.2f}s  {rel}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("lines"); l.add_argument("--voice", required=True); l.add_argument("--speed", type=float, default=1.0); l.add_argument("--only")
    au = sub.add_parser("audition"); au.add_argument("--text", required=True); au.add_argument("--voices", required=True); au.add_argument("--speed", type=float, default=1.0)
    a = p.parse_args()
    {"lines": cmd_lines, "audition": cmd_audition}[a.cmd](a)
