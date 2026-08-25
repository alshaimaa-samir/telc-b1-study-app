#!/usr/bin/env python3
"""
AI Audio Generator for Telc Deutsch B1 App
------------------------------------------
Generates studio-quality, natural multilingual MP3 audio for:
1. German Listening Transcripts & Dialogues (Native German cadence)
2. German Reading Passages
3. Bilingual Explanations (Natural English voice that fluidly pronounces German words)

Usage:
------
# Using OpenAI TTS API (Recommended for ultra-natural bilingual audio):
export OPENAI_API_KEY="your-api-key-here"
python3 scripts/generate_ai_audio.py --provider openai --voice alloy

# Or pass the key directly:
python3 scripts/generate_ai_audio.py --api-key sk-... --voice alloy
"""

import os
import sys
import json
import argparse
import ssl
import urllib.request
import urllib.error

def get_ssl_context():
    """Creates a robust SSL context that works across macOS, Linux, and Windows."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass
    try:
        return ssl.create_default_context()
    except Exception:
        return ssl._create_unverified_context()

def generate_openai_audio(text, output_path, api_key, voice="alloy", model="tts-1"):
    """Calls OpenAI TTS API and saves MP3."""
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "TelcAudioGen/1.0"
    }
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": "mp3"
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    ssl_context = get_ssl_context()

    try:
        try:
            with urllib.request.urlopen(req, context=ssl_context, timeout=60) as response:
                with open(output_path, "wb") as f:
                    f.write(response.read())
            print(f"  [OK] Saved: {output_path}")
            return True
        except (ssl.SSLCertVerificationError, urllib.error.URLError) as err:
            # Automatic fallback if macOS Python root certificates are unlinked
            if "CERTIFICATE_VERIFY_FAILED" in str(err) or "certificate verify failed" in str(err):
                fallback_ctx = ssl._create_unverified_context()
                with urllib.request.urlopen(req, context=fallback_ctx, timeout=60) as response:
                    with open(output_path, "wb") as f:
                        f.write(response.read())
                print(f"  [OK] Saved: {output_path}")
                return True
            raise err
    except urllib.error.HTTPError as e:
        print(f"  [Error] OpenAI API Error: {e.code} - {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"  [Error] {e}")
        return False

def process_model_file(model_path, audio_dir, api_key, voice="alloy"):
    with open(model_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    model_id = os.path.splitext(os.path.basename(model_path))[0]
    print(f"\nProcessing Model: {model_id.upper()} ({model_path})")

    # 1. Module 1: Leseverstehen
    # Teil 1
    t1 = data.get("leseverstehen_teil_1", {})
    for p in t1.get("passages", []):
        num = p.get("number")
        text = p.get("text", "")
        exp = p.get("explanation", "")
        if text:
            p_out = os.path.join(audio_dir, f"{model_id}_teil_1_{num}_de.mp3")
            if not os.path.exists(p_out):
                generate_openai_audio(text, p_out, api_key, voice=voice)
        if exp:
            e_out = os.path.join(audio_dir, f"{model_id}_teil_1_{num}_exp.mp3")
            if not os.path.exists(e_out):
                generate_openai_audio(exp, e_out, api_key, voice=voice)

    # Teil 2
    t2 = data.get("leseverstehen_teil_2", {})
    t2_pass = t2.get("passage", {})
    if t2_pass.get("paragraphs"):
        full_p2 = " ".join(t2_pass.get("paragraphs", []))
        p2_out = os.path.join(audio_dir, f"{model_id}_teil_2_passage.mp3")
        if not os.path.exists(p2_out):
            generate_openai_audio(full_p2, p2_out, api_key, voice=voice)
    for q in t2.get("questions", []):
        num = q.get("number")
        exp = q.get("explanation", "")
        if exp:
            e_out = os.path.join(audio_dir, f"{model_id}_teil_2_{num}_exp.mp3")
            if not os.path.exists(e_out):
                generate_openai_audio(exp, e_out, api_key, voice=voice)

    # Teil 3
    t3 = data.get("leseverstehen_teil_3", {})
    for s in t3.get("situations", []):
        num = s.get("number")
        exp = s.get("explanation", "")
        if exp:
            e_out = os.path.join(audio_dir, f"{model_id}_teil_3_{num}_exp.mp3")
            if not os.path.exists(e_out):
                generate_openai_audio(exp, e_out, api_key, voice=voice)

    # 2. Module 2: Sprachbausteine
    # Teil 1
    sb1 = data.get("sprachbausteine_teil_1", {})
    for q in sb1.get("questions", []):
        num = q.get("number")
        exp = q.get("explanation", "")
        if exp:
            e_out = os.path.join(audio_dir, f"{model_id}_sprachbausteine_1_{num}_exp.mp3")
            if not os.path.exists(e_out):
                generate_openai_audio(exp, e_out, api_key, voice=voice)

    # Teil 2
    sb2 = data.get("sprachbausteine_teil_2", {})
    for q in sb2.get("questions", []):
        num = q.get("number")
        exp = q.get("explanation", "")
        if exp:
            e_out = os.path.join(audio_dir, f"{model_id}_sprachbausteine_2_{num}_exp.mp3")
            if not os.path.exists(e_out):
                generate_openai_audio(exp, e_out, api_key, voice=voice)

    # 3. Module 3: Hörverstehen (Listening)
    # Teil 1
    hv1 = data.get("hoerverstehen_teil_1", {})
    for t in hv1.get("transcripts", []):
        num = t.get("number")
        text = t.get("text", "")
        if text:
            h1_out = os.path.join(audio_dir, f"{model_id}_hoerverstehen_1_{num}_de.mp3")
            if not os.path.exists(h1_out):
                generate_openai_audio(text, h1_out, api_key, voice=voice)
    for q in hv1.get("questions", []):
        num = q.get("number")
        exp = q.get("explanation", "")
        if exp:
            e_out = os.path.join(audio_dir, f"{model_id}_hoerverstehen_1_{num}_exp.mp3")
            if not os.path.exists(e_out):
                generate_openai_audio(exp, e_out, api_key, voice=voice)

    # Teil 2
    hv2 = data.get("hoerverstehen_teil_2", {})
    interview = hv2.get("interview_transcript", {}).get("text", "")
    if interview:
        h2_out = os.path.join(audio_dir, f"{model_id}_hoerverstehen_2_full.mp3")
        if not os.path.exists(h2_out):
            generate_openai_audio(interview, h2_out, api_key, voice=voice)
    for q in hv2.get("questions", []):
        num = q.get("number")
        exp = q.get("explanation", "")
        if exp:
            e_out = os.path.join(audio_dir, f"{model_id}_hoerverstehen_2_{num}_exp.mp3")
            if not os.path.exists(e_out):
                generate_openai_audio(exp, e_out, api_key, voice=voice)

    # Teil 3
    hv3 = data.get("hoerverstehen_teil_3", {})
    for t in hv3.get("transcripts", []):
        num = t.get("number")
        text = t.get("text", "")
        if text:
            h3_out = os.path.join(audio_dir, f"{model_id}_hoerverstehen_3_{num}_de.mp3")
            if not os.path.exists(h3_out):
                generate_openai_audio(text, h3_out, api_key, voice=voice)
    for q in hv3.get("questions", []):
        num = q.get("number")
        exp = q.get("explanation", "")
        if exp:
            e_out = os.path.join(audio_dir, f"{model_id}_hoerverstehen_3_{num}_exp.mp3")
            if not os.path.exists(e_out):
                generate_openai_audio(exp, e_out, api_key, voice=voice)

def main():
    parser = argparse.ArgumentParser(description="Generate AI MP3 Audio for Telc B1 Study App")
    parser.add_argument("--api-key", help="OpenAI API Key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--voice", default="alloy", choices=["alloy", "nova", "echo", "fable", "onyx", "shimmer"], help="OpenAI voice")
    parser.add_argument("--data-dir", default="data", help="Path to data/ directory containing exam JSON files")
    parser.add_argument("--audio-dir", default="audio", help="Output audio/ directory")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\n[!] Error: OpenAI API Key is required.")
        print("    Usage: python3 scripts/generate_ai_audio.py --api-key sk-your-key\n")
        sys.exit(1)

    os.makedirs(args.audio_dir, exist_ok=True)
    
    # Process all exam files
    files = [os.path.join(args.data_dir, f) for f in os.listdir(args.data_dir) if f.endswith(".json") and f not in ["manifest_models.json", "schema_telc_b1.json"]]
    print(f"Found {len(files)} test models to process: {[os.path.basename(f) for f in files]}")

    for f in sorted(files):
        process_model_file(f, args.audio_dir, api_key, voice=args.voice)

    print("\n[✓] Audio generation complete! All MP3 files are in:", os.path.abspath(args.audio_dir))

if __name__ == "__main__":
    main()
