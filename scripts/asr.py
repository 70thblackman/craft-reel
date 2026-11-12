#!/usr/bin/env python3
"""Word-level speech recognition for narration alignment.

    python asr.py --engine whisper --input narr/voice_edit.wav --out narr/words.json
    python asr.py --engine vosk --model <vosk-fa-model-dir> --input <16k.wav> --out <json>

Output: [{"word": "...", "start": 0.12, "end": 0.35}, ...] in seconds of the input file.
Whisper (faster-whisper) is preferred; it handles m4a/wav directly.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import wave


def load_audio_16k(path):
    # decode with ffmpeg instead of faster-whisper's PyAV path (av version drift)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path,
                        "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "pipe:1"],
                       capture_output=True)
    if r.returncode:
        sys.exit("ffmpeg could not decode " + path)
    import numpy as np
    return np.frombuffer(r.stdout, dtype=np.float32)


def whisper_words(path, model_size, lang, offset):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper is not installed: pip install faster-whisper")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    audio = load_audio_16k(path)
    segments, info = model.transcribe(
        audio, language=lang, word_timestamps=True, vad_filter=True,
        beam_size=5, condition_on_previous_text=False)
    out = []
    for seg in segments:
        for w in (seg.words or []):
            text = w.word.strip()
            if not text:
                continue
            out.append({"word": text, "start": round(w.start + offset, 3), "end": round(w.end + offset, 3)})
    print(f"{len(out)} words, {info.duration:.2f}s, lang={info.language}")
    return out


def vosk_words(path, model_dir, offset):
    try:
        from vosk import Model, KaldiRecognizer, SetLogLevel
    except ImportError:
        sys.exit("vosk is not installed: pip install vosk")
    SetLogLevel(-1)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", path,
                    "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", tmp], check=True)
    wf = wave.open(tmp, "rb")
    rec = KaldiRecognizer(Model(model_dir), 16000)
    rec.SetWords(True)
    words = []
    while True:
        data = wf.readframes(8000)
        if not data:
            break
        if rec.AcceptWaveform(data):
            words += json.loads(rec.Result()).get("result", [])
    words += json.loads(rec.FinalResult()).get("result", [])
    if tmp:
        os.unlink(tmp)
    out = [{"word": w["word"], "start": round(w["start"] + offset, 3),
            "end": round(w["end"] + offset, 3)} for w in words]
    print(f"{len(out)} words (vosk)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["whisper", "vosk"], default="whisper")
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="small", help="whisper size or vosk model dir")
    ap.add_argument("--lang", default="fa")
    ap.add_argument("--offset", type=float, default=0.0, help="seconds added to every timestamp")
    args = ap.parse_args()
    if args.engine == "whisper":
        words = whisper_words(args.input, args.model, args.lang, args.offset)
    else:
        words = vosk_words(args.input, args.model, args.offset)
    if not words:
        sys.exit("no words recognised")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(words, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
