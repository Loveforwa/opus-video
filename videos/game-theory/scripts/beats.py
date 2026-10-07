"""Prepare the BGM: cut the first N seconds, fade out, and write the beat map main.js syncs to.

    pip install librosa numpy
    python scripts/beats.py path/to/music.(mp3|mp4|wav|m4a) [--dur 60]

Writes assets/audio/bgm60.m4a and assets/audio/beats.json ({tempo, beats[], low[] @30fps}).
"""
import argparse, json, os, subprocess, tempfile
import numpy as np, librosa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("--dur", type=float, default=60.0); ap.add_argument("--start", type=float, default=0.0)
a = ap.parse_args()
out_dir = os.path.join(ROOT, "assets", "audio")
wav = os.path.join(tempfile.mkdtemp(), "cut.wav")
subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", str(a.start), "-i", a.src, "-t", str(a.dur), "-vn", "-ac", "2", "-ar", "48000", wav], check=True)
subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", wav, "-af", f"afade=t=out:st={a.dur - 1.6}:d=1.6",
                "-c:a", "aac", "-b:a", "192k", os.path.join(out_dir, "bgm60.m4a")], check=True)

y, sr = librosa.load(wav, sr=22050, mono=True)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
bt = librosa.frames_to_time(beats, sr=sr)
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=735))                    # 735 = 22050/30 → one column per video frame
low = S[librosa.fft_frequencies(sr=sr, n_fft=2048) < 150].mean(0)
low = np.clip(low / (np.percentile(low, 99) + 1e-9), 0, 1)
json.dump({"tempo": float(np.atleast_1d(tempo)[0]), "beats": [round(float(b), 3) for b in bt],
           "low": low[: int(a.dur * 30)].round(3).tolist()}, open(os.path.join(out_dir, "beats.json"), "w"))
print(f"tempo {float(np.atleast_1d(tempo)[0]):.1f} BPM · {len(bt)} beats · first beats {np.round(bt[:8], 2).tolist()}")
print("段落边界（每 16 拍）:", [round(float(bt[i]), 2) for i in range(0, len(bt), 16)])
