#!/usr/bin/env python3
"""
Comprehensive AI Audio Generator for Telc Deutsch B1 App
--------------------------------------------------------
Generates studio-quality, natural multilingual MP3 audio for:
1. Teil 1 Headings Overview (A to J in German & English)
2. German Passages, Letters, and Dialogues
3. English Literal Translations for all Passages and Articles
4. Key Vocabulary Word Pairs (German word -> English meaning)
5. Solutions, Correct Headings, and Bilingual Explanations
6. Sprachbausteine 2 Word Bank Overview (A to O in German & English)
7. Listening Module (Announcements, Radio Interviews, Everyday Dialogues)

Features:
---------
- Fast Resume: Skips any audio file that already exists by default (saving API quota and time).
- Overwrite mode: Pass --overwrite to regenerate existing files.

Usage:
------
# Normal run (skips already existing audio files):
python3 scripts/generate_ai_audio.py --api-key sk-... --voice alloy

# Force regenerate all audio files:
python3 scripts/generate_ai_audio.py --api-key sk-... --voice alloy --overwrite
"""

import os
import sys
import json
import argparse
import ssl
import urllib.request
import urllib.error
import time

stats = {
    "generated": 0,
    "skipped": 0,
    "failed": 0
}

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

def generate_openai_audio(text, output_path, api_key, voice="alloy", model="tts-1", overwrite=False):
    """Calls OpenAI TTS API and saves MP3 file. Skips if already exists unless overwrite=True."""
    global stats

    if not overwrite and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        stats["skipped"] += 1
        print(f"  [Skip] Already exists: {os.path.basename(output_path)}")
        return True

    text = text.strip()
    if not text:
        return False

    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "TelcAudioGen/2.0"
    }
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": "mp3"
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    ssl_context = get_ssl_context()

    for attempt in range(3):
        try:
            try:
                with urllib.request.urlopen(req, context=ssl_context, timeout=60) as response:
                    with open(output_path, "wb") as f:
                        f.write(response.read())
                stats["generated"] += 1
                print(f"  [OK] Generated: {os.path.basename(output_path)}")
                return True
            except (ssl.SSLCertVerificationError, urllib.error.URLError) as err:
                if "CERTIFICATE_VERIFY_FAILED" in str(err) or "certificate verify failed" in str(err):
                    fallback_ctx = ssl._create_unverified_context()
                    with urllib.request.urlopen(req, context=fallback_ctx, timeout=60) as response:
                        with open(output_path, "wb") as f:
                            f.write(response.read())
                    stats["generated"] += 1
                    print(f"  [OK] Generated: {os.path.basename(output_path)}")
                    return True
                raise err
        except urllib.error.HTTPError as e:
            print(f"  [Error] OpenAI API Error: {e.code} - {e.read().decode('utf-8')}")
            if e.code == 429:
                time.sleep(5)
                continue
            stats["failed"] += 1
            return False
        except Exception as e:
            print(f"  [Error] Attempt {attempt+1} failed for {os.path.basename(output_path)}: {e}")
            time.sleep(2)
    
    stats["failed"] += 1
    return False

def process_model_file(model_path, audio_dir, api_key, voice="alloy", overwrite=False):
    with open(model_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    model_id = os.path.splitext(os.path.basename(model_path))[0]
    model_title = data.get("title", model_id.upper())
    print(f"\n==========================================")
    print(f"Processing Model: {model_title} ({model_id})")
    print(f"==========================================")

    # ---------------------------------------------------------
    # 1. MODULE 1: LESEVERSTEHEN (READING)
    # ---------------------------------------------------------
    
    # --- TEIL 1: Zuordnung (Headings 1-5) ---
    t1 = data.get("leseverstehen_teil_1", {})
    if t1:
        headings = t1.get("headings", {})
        headings_en = t1.get("headings_en", {})
        
        # 1. Headings A-J Overview Audio
        if headings:
            overview_lines = [
                f"Modul 1: Leseverstehen. Teil 1: Zuordnung von Überschriften.",
                f"First, let's review all 10 available headings from A to J."
            ]
            for letter in sorted(headings.keys()):
                de_h = headings[letter]
                en_h = headings_en.get(letter, "")
                line = f"Überschrift {letter.upper()}: {de_h}."
                if en_h:
                    line += f" In English: {en_h}."
                overview_lines.append(line)
            
            overview_text = "\n\n".join(overview_lines)
            generate_openai_audio(overview_text, os.path.join(audio_dir, f"{model_id}_teil_1_headings_overview.mp3"), api_key, voice=voice, overwrite=overwrite)

        # 2. Passages 1-5 (German, English, Vocab, Solution)
        for p in t1.get("passages", []):
            num = p.get("number")
            text_de = p.get("text", "")
            text_en = p.get("text_en", "")
            correct_ans = str(p.get("correct_answer", "")).lower()
            explanation = p.get("explanation", "")
            vocab = p.get("vocabulary", [])

            # German passage
            if text_de:
                de_speech = f"Text {num}.\n\n{text_de}"
                generate_openai_audio(de_speech, os.path.join(audio_dir, f"{model_id}_teil_1_{num}_de.mp3"), api_key, voice=voice, overwrite=overwrite)

            # English translation
            if text_en:
                en_speech = f"English Translation for Text {num}.\n\n{text_en}"
                generate_openai_audio(en_speech, os.path.join(audio_dir, f"{model_id}_teil_1_{num}_en.mp3"), api_key, voice=voice, overwrite=overwrite)

            # Key vocabulary
            if vocab:
                vocab_lines = [f"Key vocabulary for Text {num}:"]
                for v in vocab:
                    vocab_lines.append(f"{v.get('de', '')} — {v.get('en', '')}.")
                generate_openai_audio("\n".join(vocab_lines), os.path.join(audio_dir, f"{model_id}_teil_1_{num}_vocab.mp3"), api_key, voice=voice, overwrite=overwrite)

            # Solution & Explanation
            sol_heading_de = headings.get(correct_ans, "")
            sol_heading_en = headings_en.get(correct_ans, "")
            sol_lines = [f"Solution for Text {num}: Überschrift {correct_ans.upper()}."]
            if sol_heading_de:
                sol_lines.append(f"{sol_heading_de}.")
            if sol_heading_en:
                sol_lines.append(f"In English: {sol_heading_en}.")
            if explanation:
                sol_lines.append(f"Explanation: {explanation}")
            
            sol_text = " ".join(sol_lines)
            generate_openai_audio(sol_text, os.path.join(audio_dir, f"{model_id}_teil_1_{num}_sol.mp3"), api_key, voice=voice, overwrite=overwrite)
            # Maintain backward compatibility
            generate_openai_audio(explanation or sol_text, os.path.join(audio_dir, f"{model_id}_teil_1_{num}_exp.mp3"), api_key, voice=voice, overwrite=overwrite)

    # --- TEIL 2: Artikel (Article & Questions 6-10) ---
    t2 = data.get("leseverstehen_teil_2", {})
    if t2:
        p2 = t2.get("passage", {})
        headline_de = p2.get("headline", "")
        headline_en = p2.get("headline_en", headline_de)
        paragraphs = p2.get("paragraphs", [])
        text_en = p2.get("text_en", "")

        # German Article
        if paragraphs:
            art_de = f"Teil 2: Zeitungsartikel.\n\nTitel: {headline_de}.\n\n" + "\n\n".join(paragraphs)
            generate_openai_audio(art_de, os.path.join(audio_dir, f"{model_id}_teil_2_passage.mp3"), api_key, voice=voice, overwrite=overwrite)
            generate_openai_audio(art_de, os.path.join(audio_dir, f"{model_id}_teil_2_passage_de.mp3"), api_key, voice=voice, overwrite=overwrite)

        # English Translation
        if text_en:
            art_en = f"English Translation.\n\nTitle: {headline_en}.\n\n{text_en}"
            generate_openai_audio(art_en, os.path.join(audio_dir, f"{model_id}_teil_2_passage_en.mp3"), api_key, voice=voice, overwrite=overwrite)

        # Questions 6-10
        for q in t2.get("questions", []):
            num = q.get("number")
            q_text = q.get("question", "")
            options = q.get("options", {})
            correct_ans = str(q.get("correct_answer", "")).lower()
            explanation = q.get("explanation", "")

            # Question + Options prompt in German
            q_lines = [f"Frage {num}: {q_text}."]
            for opt_k in ["a", "b", "c"]:
                if opt_k in options:
                    q_lines.append(f"Option {opt_k.upper()}: {options[opt_k]}.")
            q_prompt_de = "\n".join(q_lines)
            generate_openai_audio(q_prompt_de, os.path.join(audio_dir, f"{model_id}_teil_2_{num}_de.mp3"), api_key, voice=voice, overwrite=overwrite)

            # Solution & Explanation
            opt_chosen = options.get(correct_ans, "")
            sol_text = f"Solution for Question {num}: Option {correct_ans.upper()}, {opt_chosen}. Explanation: {explanation}"
            generate_openai_audio(sol_text, os.path.join(audio_dir, f"{model_id}_teil_2_{num}_sol.mp3"), api_key, voice=voice, overwrite=overwrite)
            generate_openai_audio(explanation or sol_text, os.path.join(audio_dir, f"{model_id}_teil_2_{num}_exp.mp3"), api_key, voice=voice, overwrite=overwrite)

    # --- TEIL 3: Anzeigen & Situationen (Questions 11-20) ---
    t3 = data.get("leseverstehen_teil_3", {})
    if t3:
        ads = t3.get("advertisements", {})
        for s in t3.get("situations", []):
            num = s.get("number")
            sit_de = s.get("text", "")
            sit_en = s.get("text_en", "")
            correct_ans = str(s.get("correct_answer", "")).lower()
            explanation = s.get("explanation", "")

            # Situation prompt
            sit_speech = f"Situation {num}: {sit_de}."
            if sit_en:
                sit_speech += f"\nIn English: {sit_en}."
            generate_openai_audio(sit_speech, os.path.join(audio_dir, f"{model_id}_teil_3_{num}_de.mp3"), api_key, voice=voice, overwrite=overwrite)

            # Solution & Explanation
            if correct_ans == "x":
                sol_text = f"Solution for Situation {num}: Keine passende Anzeige gefunden (Option X). Explanation: {explanation}"
            else:
                matched_ad = ads.get(correct_ans, {})
                ad_title = matched_ad.get("title", f"Anzeige {correct_ans.upper()}")
                sol_text = f"Solution for Situation {num}: Passende Anzeige ist {correct_ans.upper()}, {ad_title}. Explanation: {explanation}"
            
            generate_openai_audio(sol_text, os.path.join(audio_dir, f"{model_id}_teil_3_{num}_sol.mp3"), api_key, voice=voice, overwrite=overwrite)
            generate_openai_audio(explanation or sol_text, os.path.join(audio_dir, f"{model_id}_teil_3_{num}_exp.mp3"), api_key, voice=voice, overwrite=overwrite)

    # ---------------------------------------------------------
    # 2. MODULE 2: SPRACHBAUSTEINE (LANGUAGE ELEMENTS)
    # ---------------------------------------------------------
    
    # --- TEIL 1: Brief Cloze (Questions 21-30) ---
    sb1 = data.get("sprachbausteine_teil_1", {})
    if sb1:
        passage1 = sb1.get("passage", {}) or sb1.get("letter", {})
        letter_de = passage1.get("text", "")
        letter_en = passage1.get("text_en", "")

        if letter_de:
            generate_openai_audio(f"Modul 2: Sprachbausteine. Teil 1: Brief.\n\n{letter_de}", os.path.join(audio_dir, f"{model_id}_sprachbausteine_1_letter_de.mp3"), api_key, voice=voice, overwrite=overwrite)
        if letter_en:
            generate_openai_audio(f"English translation of the letter.\n\n{letter_en}", os.path.join(audio_dir, f"{model_id}_sprachbausteine_1_letter_en.mp3"), api_key, voice=voice, overwrite=overwrite)

        for q in sb1.get("questions", []):
            num = q.get("number")
            options = q.get("options", {})
            correct_ans = str(q.get("correct_answer", "")).lower()
            explanation = q.get("explanation", "")
            opt_chosen = options.get(correct_ans, "")

            sol_text = f"Lösung für Lücke {num}: Option {correct_ans.upper()}, {opt_chosen}. Explanation: {explanation}"
            generate_openai_audio(sol_text, os.path.join(audio_dir, f"{model_id}_sprachbausteine_1_{num}_sol.mp3"), api_key, voice=voice, overwrite=overwrite)
            generate_openai_audio(explanation or sol_text, os.path.join(audio_dir, f"{model_id}_sprachbausteine_1_{num}_exp.mp3"), api_key, voice=voice, overwrite=overwrite)

    # --- TEIL 2: Wortschatz (Questions 31-40) ---
    sb2 = data.get("sprachbausteine_teil_2", {})
    if sb2:
        passage2 = sb2.get("passage", {})
        text_de = (passage2.get("headline", "") + "\n\n" + passage2.get("text", "")).strip()
        text_en = passage2.get("text_en", "")
        options_bank = sb2.get("options", {})

        # Word bank overview (A to O)
        if options_bank:
            wb_lines = [
                "Teil 2: Lückentext mit Wortschatz.",
                "First, let's review all options from the word bank from A to O:"
            ]
            for letter in sorted(options_bank.keys()):
                wb_lines.append(f"Option {letter.upper()}: {options_bank[letter]}.")
            generate_openai_audio("\n".join(wb_lines), os.path.join(audio_dir, f"{model_id}_sprachbausteine_2_wordbank_overview.mp3"), api_key, voice=voice, overwrite=overwrite)

        if text_de:
            generate_openai_audio(f"Text:\n\n{text_de}", os.path.join(audio_dir, f"{model_id}_sprachbausteine_2_text_de.mp3"), api_key, voice=voice, overwrite=overwrite)
        if text_en:
            generate_openai_audio(f"English translation:\n\n{text_en}", os.path.join(audio_dir, f"{model_id}_sprachbausteine_2_text_en.mp3"), api_key, voice=voice, overwrite=overwrite)

        for q in sb2.get("questions", []):
            num = q.get("number")
            correct_ans = str(q.get("correct_answer", "")).lower()
            explanation = q.get("explanation", "")
            word_chosen = options_bank.get(correct_ans, "")

            sol_text = f"Lösung für Lücke {num}: Option {correct_ans.upper()}, {word_chosen}. Explanation: {explanation}"
            generate_openai_audio(sol_text, os.path.join(audio_dir, f"{model_id}_sprachbausteine_2_{num}_sol.mp3"), api_key, voice=voice, overwrite=overwrite)
            generate_openai_audio(explanation or sol_text, os.path.join(audio_dir, f"{model_id}_sprachbausteine_2_{num}_exp.mp3"), api_key, voice=voice, overwrite=overwrite)

    # ---------------------------------------------------------
    # 3. MODULE 3: HÖRVERSTEHEN (LISTENING)
    # ---------------------------------------------------------
    
    # --- TEIL 1: Ansagen (Questions 41-45) ---
    hv1 = data.get("hoerverstehen_teil_1", {})
    if hv1:
        for t in hv1.get("transcripts", []):
            num = t.get("number")
            t_text = t.get("text", "")
            if t_text:
                generate_openai_audio(t_text, os.path.join(audio_dir, f"{model_id}_hoerverstehen_1_{num}_de.mp3"), api_key, voice=voice, overwrite=overwrite)

        for q in hv1.get("questions", []):
            num = q.get("number")
            stmt = q.get("statement", "")
            stmt_en = q.get("statement_en", "")
            ans = str(q.get("correct_answer", "")).lower()
            is_true = ans in ["+", "richtig", "true", "t"]
            explanation = q.get("explanation", "")

            sol_text = f"Frage {num}: Aussage: {stmt}."
            if stmt_en:
                sol_text += f" In English: {stmt_en}."
            sol_text += f" Lösung: {'Richtig (+)' if is_true else 'Falsch (-)'}. Explanation: {explanation}"
            
            generate_openai_audio(sol_text, os.path.join(audio_dir, f"{model_id}_hoerverstehen_1_{num}_sol.mp3"), api_key, voice=voice, overwrite=overwrite)
            generate_openai_audio(explanation or sol_text, os.path.join(audio_dir, f"{model_id}_hoerverstehen_1_{num}_exp.mp3"), api_key, voice=voice, overwrite=overwrite)

    # --- TEIL 2: Radio Interview (Questions 46-55) ---
    hv2 = data.get("hoerverstehen_teil_2", {})
    if hv2:
        interview = hv2.get("interview_transcript", {}).get("text", "")
        if interview:
            generate_openai_audio(interview, os.path.join(audio_dir, f"{model_id}_hoerverstehen_2_full.mp3"), api_key, voice=voice, overwrite=overwrite)

        for q in hv2.get("questions", []):
            num = q.get("number")
            stmt = q.get("statement", "")
            stmt_en = q.get("statement_en", "")
            ans = str(q.get("correct_answer", "")).lower()
            is_true = ans in ["+", "richtig", "true", "t"]
            explanation = q.get("explanation", "")

            sol_text = f"Aussage {num}: {stmt}."
            if stmt_en:
                sol_text += f" In English: {stmt_en}."
            sol_text += f" Lösung: {'Richtig (+)' if is_true else 'Falsch (-)'}. Explanation: {explanation}"

            generate_openai_audio(sol_text, os.path.join(audio_dir, f"{model_id}_hoerverstehen_2_{num}_sol.mp3"), api_key, voice=voice, overwrite=overwrite)
            generate_openai_audio(explanation or sol_text, os.path.join(audio_dir, f"{model_id}_hoerverstehen_2_{num}_exp.mp3"), api_key, voice=voice, overwrite=overwrite)

    # --- TEIL 3: Alltagsgespräche (Questions 56-60) ---
    hv3 = data.get("hoerverstehen_teil_3", {})
    if hv3:
        for t in hv3.get("transcripts", []):
            num = t.get("number")
            t_text = t.get("text", "")
            if t_text:
                generate_openai_audio(t_text, os.path.join(audio_dir, f"{model_id}_hoerverstehen_3_{num}_de.mp3"), api_key, voice=voice, overwrite=overwrite)

        for q in hv3.get("questions", []):
            num = q.get("number")
            stmt = q.get("statement", "")
            stmt_en = q.get("statement_en", "")
            ans = str(q.get("correct_answer", "")).lower()
            is_true = ans in ["+", "richtig", "true", "t"]
            explanation = q.get("explanation", "")

            sol_text = f"Gespräch {num}: Aussage: {stmt}."
            if stmt_en:
                sol_text += f" In English: {stmt_en}."
            sol_text += f" Lösung: {'Richtig (+)' if is_true else 'Falsch (-)'}. Explanation: {explanation}"

            generate_openai_audio(sol_text, os.path.join(audio_dir, f"{model_id}_hoerverstehen_3_{num}_sol.mp3"), api_key, voice=voice, overwrite=overwrite)
            generate_openai_audio(explanation or sol_text, os.path.join(audio_dir, f"{model_id}_hoerverstehen_3_{num}_exp.mp3"), api_key, voice=voice, overwrite=overwrite)

def main():
    parser = argparse.ArgumentParser(description="Comprehensive AI MP3 Audio Generator for Telc B1 Study App")
    parser.add_argument("--api-key", help="OpenAI API Key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--voice", default="alloy", choices=["alloy", "nova", "echo", "fable", "onyx", "shimmer"], help="OpenAI voice")
    parser.add_argument("--data-dir", default="data", help="Path to data/ directory containing exam JSON files")
    parser.add_argument("--audio-dir", default="audio", help="Output audio/ directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing audio files instead of skipping them")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\n[!] Error: OpenAI API Key is required.")
        print("    Usage: python3 scripts/generate_ai_audio.py --api-key sk-your-key\n")
        sys.exit(1)

    os.makedirs(args.audio_dir, exist_ok=True)
    
    files = [os.path.join(args.data_dir, f) for f in os.listdir(args.data_dir) if f.endswith(".json") and f not in ["manifest_models.json", "schema_telc_b1.json"]]
    print(f"Found {len(files)} test models: {[os.path.basename(f) for f in files]}")
    print(f"Overwrite existing files: {args.overwrite}")

    for f in sorted(files):
        process_model_file(f, args.audio_dir, api_key, voice=args.voice, overwrite=args.overwrite)

    print("\n" + "="*50)
    print("AUDIO GENERATION SUMMARY")
    print("="*50)
    print(f"  • Newly Generated: {stats['generated']} files")
    print(f"  • Skipped Existing: {stats['skipped']} files")
    print(f"  • Failed:           {stats['failed']} files")
    print(f"  • Output Directory: {os.path.abspath(args.audio_dir)}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()

