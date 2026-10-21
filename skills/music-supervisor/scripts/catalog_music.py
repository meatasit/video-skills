#!/usr/bin/env python3
"""catalog_music.py — วัดค่าเพลงในคลังแล้วเขียน library.json

    python catalog_music.py D:\\music-library            # เพิ่ม/อัปเดตเฉพาะไฟล์ที่เปลี่ยน
    python catalog_music.py D:\\music-library --force    # วัดใหม่ทั้งหมด
    python catalog_music.py D:\\music-library --summary  # แค่สรุป ไม่วัด

ต้องมี: pip install librosa soundfile numpy  (และ ffmpeg ใน PATH สำหรับ mp3/m4a)
ไม่ tag mood — ส่วนนั้น Claude เขียนใน tags.md ตาม SKILL.md
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

AUDIO_EXT = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"}
ANALYSIS_SR = 22050


def file_hash(path, chunk=1 << 20):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()[:16]


def ffprobe_meta(path):
    """title/artist/genre/duration จาก container — ไม่มีก็ว่าง"""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
            capture_output=True, text=True, timeout=30,
        )
        fmt = json.loads(out.stdout or "{}").get("format", {})
        tags = {k.lower(): v for k, v in fmt.get("tags", {}).items()}
        return {
            "title": tags.get("title", ""),
            "artist": tags.get("artist", ""),
            "genre": tags.get("genre", ""),
            "comment": tags.get("comment", "")[:200],
            "duration": float(fmt.get("duration", 0) or 0),
        }
    except Exception:
        return {"title": "", "artist": "", "genre": "", "comment": "", "duration": 0.0}


def load_audio(path):
    import librosa
    try:
        y, sr = librosa.load(path, sr=ANALYSIS_SR, mono=True)
        return y, sr
    except Exception:
        # librosa/soundfile อ่าน mp3/m4a บางไฟล์ไม่ได้ → แปลงผ่าน ffmpeg ก่อน
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav = tmp.name
        subprocess.run(
            ["ffmpeg", "-v", "quiet", "-y", "-i", path, "-ac", "1", "-ar", str(ANALYSIS_SR), wav],
            check=True, timeout=300,
        )
        try:
            y, sr = librosa.load(wav, sr=ANALYSIS_SR, mono=True)
        finally:
            os.unlink(wav)
        return y, sr


def analyze(path):
    import librosa
    import numpy as np

    y, sr = load_audio(path)
    duration = float(len(y) / sr)

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])

    hop = sr  # 1 วินาทีต่อจุด
    rms = librosa.feature.rms(y=y, frame_length=hop, hop_length=hop)[0]
    if rms.max() > 0:
        energy = (rms / rms.max()).astype(float)
    else:
        energy = rms.astype(float)
    energy_curve = [round(float(v), 3) for v in energy]

    # intro เงียบ: วินาทีแรกที่ energy > 0.15
    intro_end = next((i for i, v in enumerate(energy_curve) if v > 0.15), 0)

    # drop: จุดที่ค่าเฉลี่ย 4 วิถัดไปสูงกว่า 4 วิก่อนหน้ามากที่สุด (ข้าม 8 วิแรก)
    drop_at, best = None, 0.0
    w = 4
    for i in range(max(w, 8), len(energy_curve) - w):
        before = sum(energy_curve[i - w:i]) / w
        after = sum(energy_curve[i:i + w]) / w
        gain = after - before
        if gain > best and after > 0.5:
            best, drop_at = gain, i
    # section ที่ energy สูงสุดต่อเนื่อง (สำหรับวาง hook)
    peak_at = int(np.argmax(energy)) if len(energy) else 0

    mean_e = float(np.mean(energy)) if len(energy) else 0.0
    # energy 1–5 แบบหยาบจาก mean + tempo (Claude ปรับทีหลังใน tags.md ได้)
    e5 = 1 + round(min(1.0, mean_e * 0.7 + (tempo / 180) * 0.3) * 4)

    # loopable คร่าวๆ: หัว-ท้าย energy ใกล้กันและไม่มี intro เงียบยาว
    tail = energy_curve[-3:] if len(energy_curve) >= 3 else energy_curve
    head = energy_curve[intro_end:intro_end + 3] or energy_curve[:3]
    loopable = bool(intro_end <= 1 and head and tail and abs(sum(head) / len(head) - sum(tail) / len(tail)) < 0.2)

    # spectral centroid เฉลี่ย → "สว่าง/ทึบ" ช่วยเดา mood
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    brightness = float(np.mean(cent)) if len(cent) else 0.0

    return {
        "duration_s": round(duration, 1),
        "bpm": round(tempo),
        "energy_1_5": int(e5),
        "energy_mean": round(mean_e, 3),
        "intro_silence_s": int(intro_end),
        "drop_at_s": drop_at,
        "peak_at_s": int(peak_at),
        "loopable_guess": loopable,
        "brightness_hz": round(brightness),
        "energy_curve_1s": energy_curve,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("library", help="โฟลเดอร์คลังเพลง")
    ap.add_argument("--force", action="store_true", help="วัดใหม่ทุกไฟล์")
    ap.add_argument("--summary", action="store_true", help="สรุปจาก library.json เดิมโดยไม่วัด")
    args = ap.parse_args()

    lib = os.path.abspath(args.library)
    out_path = os.path.join(lib, "library.json")
    existing = {}
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            existing = {t["file"]: t for t in json.load(f).get("tracks", [])}

    files = sorted(
        f for f in os.listdir(lib)
        if os.path.splitext(f)[1].lower() in AUDIO_EXT and not f.startswith(".")
    )

    if args.summary:
        tracks = list(existing.values())
    else:
        try:
            import librosa  # noqa: F401
        except ImportError:
            sys.exit("ต้องติดตั้งก่อน: pip install librosa soundfile numpy")
        tracks, added, skipped = [], 0, 0
        for i, name in enumerate(files, 1):
            path = os.path.join(lib, name)
            h = file_hash(path)
            prev = existing.get(name)
            if prev and prev.get("hash") == h and not args.force:
                tracks.append(prev)
                skipped += 1
                continue
            print(f"[{i}/{len(files)}] {name}", flush=True)
            try:
                a = analyze(path)
            except Exception as e:  # ไฟล์เสีย/ฟอร์แมตแปลก ข้ามแต่บันทึกไว้
                print(f"   ข้าม: {e}")
                tracks.append({"file": name, "hash": h, "error": str(e)[:120]})
                continue
            meta = ffprobe_meta(path)
            if not a["duration_s"] and meta["duration"]:
                a["duration_s"] = round(meta["duration"], 1)
            tracks.append({"file": name, "hash": h, "meta": meta, **a})
            added += 1
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "library": lib, "tracks": tracks},
                f, ensure_ascii=False, indent=1,
            )
        print(f"\nเขียน {out_path}: ใหม่/อัปเดต {added}, ใช้ค่าเดิม {skipped}")

    ok = [t for t in tracks if "error" not in t]
    print(f"\nเพลงทั้งหมด {len(ok)} (เสีย {len(tracks) - len(ok)})")
    if ok:
        bpm = sorted(t["bpm"] for t in ok)
        print(f"BPM {bpm[0]}–{bpm[-1]} (กลาง {bpm[len(bpm) // 2]})")
        by_e = {}
        for t in ok:
            by_e[t["energy_1_5"]] = by_e.get(t["energy_1_5"], 0) + 1
        print("energy:", " ".join(f"{k}:{by_e[k]}" for k in sorted(by_e)))
        print(f"loopable (เดา): {sum(1 for t in ok if t.get('loopable_guess'))}")
        print(f"ความยาวรวม {sum(t['duration_s'] for t in ok) / 60:.0f} นาที")
    tags_path = os.path.join(lib, "tags.md")
    tagged = set()
    if os.path.exists(tags_path):
        with open(tags_path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("|") and not line.startswith("| ไฟล์") and "---" not in line:
                    tagged.add(line.split("|")[1].strip())
    untagged = [t["file"] for t in ok if t["file"] not in tagged]
    if untagged:
        print(f"\nยังไม่ได้ tag mood ใน tags.md ({len(untagged)}):")
        for n in untagged:
            print("  -", n)


if __name__ == "__main__":
    main()
