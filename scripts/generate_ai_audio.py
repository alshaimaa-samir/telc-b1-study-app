#!/usr/bin/env python3
"""
TELC B1 AI Audio Generator
==========================
Generates high-quality German & English audio files using OpenAI Text-to-Speech API.

Supports:
- Running per specific test model (e.g. --model eva1, --model petra, --model sophie)
- Running for multiple comma-separated models (e.g. --model eva1,petra)
- Running for all discovered models (--model all)
- Filtering by section/module (--section hoerverstehen / leseverstehen / sprachbausteine / all)
- Listing all available test models in data/ (--list-models)
- Resuming without regenerating existing files (--overwrite to force recreate)
- Automatic manifest update (data/manifest_models.json)
- Exponential backoff on OpenAI rate limits (HTTP 429)

Usage:
  python3 scripts/generate_ai_audio.py --list-models
  python3 scripts/generate_ai_audio.py --model eva1 --section hoerverstehen
  python3 scripts/generate_ai_audio.py --model eva1,petra --voice alloy
  python3 scripts/generate_ai_audio.py --model all --overwrite
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
MANIFEST_PATH = os.path.join(DATA_DIR, "manifest_models.json")

stats = {
    "generated": 0,
    "skipped": 0,
    "failed": 0
}

def get_available_models():
    """Discover all test model JSON files in data/ directory."""
    models = []
    if not os.path.exists(DATA_DIR):
        return models
    for filename in sorted(os.listdir(DATA_DIR)):
        if filename.endswith(".json") and not filename.startswith("schema") and filename != "manifest_models.json":
            model_id = os.path.splitext(filename)[0]
            filepath = os.path.join(DATA_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    title = data.get("title", model_id)
                    description = data.get("description", "")
            except Exception:
                title = model_id
                description = ""
            models.append({
                "id": model_id,
                "file": filename,
                "path": filepath,
                "title": title,
                "description": description
            })
    return models

def generate_openai_audio(text, output_path, api_key, voice="alloy", model="tts-1", overwrite=False, delay=0.05):
    """Generate MP3 audio file from text using OpenAI TTS endpoint."""
    if not text or not text.strip():
        return False

    if os.path.exists(output_path) and not overwrite:
        print(f"  [Skip] Existing: {os.path.basename(output_path)}")
        stats["skipped"] += 1
        return True

    text = text.strip()
    if len(text) > 4000:
        text = text[:3990] + "..."

    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": "mp3"
    }

    max_retries = 4
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                if resp.status == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, "wb") as f_out:
                        f_out.write(resp.read())
                    print(f"  [Generated] {os.path.basename(output_path)}")
                    stats["generated"] += 1
                    time.sleep(delay)
                    return True
                else:
                    print(f"  [Error] HTTP {resp.status} for {os.path.basename(output_path)}")
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="ignore")
            print(f"  [HTTP Error {e.code}] Attempt {attempt+1}/{max_retries} for {os.path.basename(output_path)}: {err_msg[:120]}")
            if e.code == 429:
                wait_sec = (attempt + 1) * 6
                print(f"  [Rate Limit] Waiting {wait_sec}s before retry...")
                time.sleep(wait_sec)
                continue
            stats["failed"] += 1
            return False
        except Exception as e:
            print(f"  [Error] Attempt {attempt+1}/{max_retries} for {os.path.basename(output_path)}: {e}")
            time.sleep(2)

    stats["failed"] += 1
    return False

def process_model_file(model_path, audio_dir, api_key, voice="alloy", tts_model="tts-1", overwrite=False, section="all", delay=0.05):
    """Process all text items for a given test model JSON file."""
    with open(model_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    model_id = os.path.splitext(os.path.basename(model_path))[0]
    model_title = data.get("title", model_id.upper())
    sec_filter = (section or "all").lower()

    print("\n" + "=" * 55)
    print(f"Processing Model: {model_title} ({model_id})")
    print(f"Section Scope:    {sec_filter.upper()}")
    print(f"Voice / Model:    {voice} / {tts_model}")
    print("=" * 55)

    run_leseverstehen = sec_filter in ["all", "leseverstehen", "reading", "lesen"]
    run_sprachbausteine = sec_filter in ["all", "sprachbausteine", "grammar", "language"]
    run_hoerverstehen = sec_filter in ["all", "hoerverstehen", "listening", "hoeren", "audio"]

    # 1. LESEVERSTEHEN
    if run_leseverstehen:
        # Teil 1
        t1 = data.get("leseverstehen_teil_1", {})
        if t1:
            headings = t1.get("headings", {})
            headings_en = t1.get("headings_en", {})
            if headings:
                overview_lines = [
                    "Modul 1: Leseverstehen. Teil 1: Zuordnung von Überschriften.",
                    "First, let us review all 10 available headings from A to J."
                ]
                for letter in sorted(headings.keys()):
                    de_h = headings[letter]
                    en_h = headings_en.get(letter, "")
                    line = f"Überschrift {letter.upper()}: {de_h}."
                    if en_h:
                        line += f" In English: {en_h}."
                    overview_lines.append(line)
                overview_text = "\n\n".join(overview_lines)
                generate_openai_audio(overview_text, os.path.join(audio_dir, f"{model_id}_teil_1_headings_overview.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

            for p in t1.get("passages", []):
                num = p.get("number")
                text_de = p.get("text", "")
                text_en = p.get("text_en", "")
                correct_ans = str(p.get("correct_answer", "")).lower()
                explanation = p.get("explanation", "")
                vocab = p.get("vocabulary", [])

                if text_de:
                    generate_openai_audio(f"Text {num}.\n\n{text_de}", os.path.join(audio_dir, f"{model_id}_teil_1_{num}_de.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
                if text_en:
                    generate_openai_audio(f"English Translation for Text {num}.\n\n{text_en}", os.path.join(audio_dir, f"{model_id}_teil_1_{num}_en.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
                if vocab:
                    vocab_lines = [f"Key vocabulary for Text {num}:"]
                    for v in vocab:
                        vocab_lines.append(f"{v.get('de', '')} - {v.get('en', '')}.")
                    generate_openai_audio("\n".join(vocab_lines), os.path.join(audio_dir, f"{model_id}_teil_1_{num}_vocab.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

                sol_lines = [f"Lösung für Text {num}: Die richtige Überschrift ist Buchstabe {correct_ans.upper()}."]
                matching_de = headings.get(correct_ans, "")
                if matching_de:
                    sol_lines.append(f"Überschrift: {matching_de}.")
                if explanation:
                    sol_lines.append(f"Erklärung: {explanation}")
                generate_openai_audio("\n\n".join(sol_lines), os.path.join(audio_dir, f"{model_id}_teil_1_{num}_solution.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

        # Teil 2
        t2 = data.get("leseverstehen_teil_2", {})
        if t2:
            title_de = t2.get("title", "")
            title_en = t2.get("title_en", "")
            text_de = t2.get("text", "")
            text_en = t2.get("text_en", "")
            vocab = t2.get("vocabulary", [])

            if text_de:
                generate_openai_audio(f"Modul 1: Leseverstehen. Teil 2: Artikel.\n\nTitel: {title_de}.\n\n{text_de}", os.path.join(audio_dir, f"{model_id}_teil_2_article_de.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
            if text_en:
                generate_openai_audio(f"English translation of the article.\n\nTitle: {title_en}.\n\n{text_en}", os.path.join(audio_dir, f"{model_id}_teil_2_article_en.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
            if vocab:
                v_lines = ["Key vocabulary for Leseverstehen Teil 2:"]
                for v in vocab:
                    v_lines.append(f"{v.get('de', '')} - {v.get('en', '')}.")
                generate_openai_audio("\n".join(v_lines), os.path.join(audio_dir, f"{model_id}_teil_2_vocab.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

            for q in t2.get("questions", []):
                num = q.get("number")
                q_de = q.get("question", "")
                q_en = q.get("question_en", "")
                opts = q.get("options", {})
                opts_en = q.get("options_en", {})
                correct = str(q.get("correct_answer", "")).lower()
                explanation = q.get("explanation", "")

                q_de_lines = [f"Frage {num}: {q_de}"]
                for opt_k in ["a", "b", "c"]:
                    if opt_k in opts:
                        q_de_lines.append(f"Option {opt_k.upper()}: {opts[opt_k]}")
                generate_openai_audio("\n".join(q_de_lines), os.path.join(audio_dir, f"{model_id}_teil_2_q{num}_de.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

                q_en_lines = [f"Question {num}: {q_en}"]
                for opt_k in ["a", "b", "c"]:
                    if opt_k in opts_en:
                        q_en_lines.append(f"Option {opt_k.upper()}: {opts_en[opt_k]}")
                generate_openai_audio("\n".join(q_en_lines), os.path.join(audio_dir, f"{model_id}_teil_2_q{num}_en.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

                correct_text = opts.get(correct, "")
                sol_lines = [f"Lösung für Frage {num}: Die richtige Antwort ist {correct.upper()}: {correct_text}."]
                if explanation:
                    sol_lines.append(f"Erklärung: {explanation}")
                generate_openai_audio("\n\n".join(sol_lines), os.path.join(audio_dir, f"{model_id}_teil_2_q{num}_solution.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

        # Teil 3
        t3 = data.get("leseverstehen_teil_3", {})
        if t3:
            situations = t3.get("situations", [])
            adverts = t3.get("advertisements", {})
            adverts_en = t3.get("advertisements_en", {})

            for s in situations:
                num = s.get("number")
                s_de = s.get("text", "")
                s_en = s.get("text_en", "")
                correct = str(s.get("correct_answer", "")).lower()
                explanation = s.get("explanation", "")
                vocab = s.get("vocabulary", [])

                if s_de:
                    generate_openai_audio(f"Situation {num}: {s_de}", os.path.join(audio_dir, f"{model_id}_teil_3_{num}_de.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
                if s_en:
                    generate_openai_audio(f"English translation for Situation {num}: {s_en}", os.path.join(audio_dir, f"{model_id}_teil_3_{num}_en.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
                if vocab:
                    v_lines = [f"Key vocabulary for Situation {num}:"]
                    for v in vocab:
                        v_lines.append(f"{v.get('de', '')} - {v.get('en', '')}.")
                    generate_openai_audio("\n".join(v_lines), os.path.join(audio_dir, f"{model_id}_teil_3_{num}_vocab.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

                if correct == "x":
                    sol_text = f"Lösung für Situation {num}: Keine passende Anzeige gefunden. Die richtige Antwort ist Buchstabe X."
                else:
                    adv_content = adverts.get(correct, "")
                    sol_text = f"Lösung für Situation {num}: Die passende Anzeige ist Buchstabe {correct.upper()}.\n\nAnzeigentext: {adv_content}"
                if explanation:
                    sol_text += f"\n\nErklärung: {explanation}"
                generate_openai_audio(sol_text, os.path.join(audio_dir, f"{model_id}_teil_3_{num}_solution.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

            for letter, adv_text in adverts.items():
                let_lower = letter.lower()
                generate_openai_audio(f"Anzeige {letter.upper()}:\n\n{adv_text}", os.path.join(audio_dir, f"{model_id}_teil_3_ad_{let_lower}_de.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
                adv_en = adverts_en.get(letter, "")
                if adv_en:
                    generate_openai_audio(f"English translation for Advertisement {letter.upper()}:\n\n{adv_en}", os.path.join(audio_dir, f"{model_id}_teil_3_ad_{let_lower}_en.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

    # 2. SPRACHBAUSTEINE
    if run_sprachbausteine:
        sp1 = data.get("sprachbausteine_teil_1", {})
        if sp1:
            text_de = sp1.get("text", "")
            text_en = sp1.get("text_en", "")
            vocab = sp1.get("vocabulary", [])

            if text_de:
                generate_openai_audio(f"Modul 2: Sprachbausteine. Teil 1.\n\n{text_de}", os.path.join(audio_dir, f"{model_id}_sprachbausteine_1_letter_de.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
            if text_en:
                generate_openai_audio(f"English translation for Sprachbausteine Teil 1 letter.\n\n{text_en}", os.path.join(audio_dir, f"{model_id}_sprachbausteine_1_letter_en.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
            if vocab:
                v_lines = ["Key vocabulary for Sprachbausteine Teil 1:"]
                for v in vocab:
                    v_lines.append(f"{v.get('de', '')} - {v.get('en', '')}.")
                generate_openai_audio("\n".join(v_lines), os.path.join(audio_dir, f"{model_id}_sprachbausteine_1_vocab.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

            for q in sp1.get("questions", []):
                num = q.get("number")
                opts = q.get("options", {})
                correct = str(q.get("correct_answer", "")).lower()
                explanation = q.get("explanation", "")

                q_lines = [f"Lücke {num}:"]
                for opt_k in ["a", "b", "c"]:
                    if opt_k in opts:
                        q_lines.append(f"Option {opt_k.upper()}: {opts[opt_k]}")
                generate_openai_audio("\n".join(q_lines), os.path.join(audio_dir, f"{model_id}_sprachbausteine_1_q{num}_options.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

                correct_val = opts.get(correct, "")
                sol_lines = [f"Lösung für Lücke {num}: Die richtige Antwort ist {correct.upper()}: {correct_val}."]
                if explanation:
                    sol_lines.append(f"Grammatikerklärung: {explanation}")
                generate_openai_audio("\n\n".join(sol_lines), os.path.join(audio_dir, f"{model_id}_sprachbausteine_1_q{num}_explanation.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

        sp2 = data.get("sprachbausteine_teil_2", {})
        if sp2:
            text_de = sp2.get("text", "")
            text_en = sp2.get("text_en", "")
            words_pool = sp2.get("words_pool", {})
            words_pool_en = sp2.get("words_pool_en", {})
            vocab = sp2.get("vocabulary", [])

            if text_de:
                generate_openai_audio(f"Modul 2: Sprachbausteine. Teil 2.\n\n{text_de}", os.path.join(audio_dir, f"{model_id}_sprachbausteine_2_text_de.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
            if text_en:
                generate_openai_audio(f"English translation for Sprachbausteine Teil 2 text.\n\n{text_en}", os.path.join(audio_dir, f"{model_id}_sprachbausteine_2_text_en.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
            if words_pool:
                w_lines = ["Wortpool für Sprachbausteine Teil 2: Von Buchstabe A bis O."]
                for letter in sorted(words_pool.keys()):
                    w_de = words_pool[letter]
                    w_en = words_pool_en.get(letter, "")
                    line = f"Wort {letter.upper()}: {w_de}."
                    if w_en:
                        line += f" Meaning: {w_en}."
                    w_lines.append(line)
                generate_openai_audio("\n".join(w_lines), os.path.join(audio_dir, f"{model_id}_sprachbausteine_2_wordpool.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
            if vocab:
                v_lines = ["Key vocabulary for Sprachbausteine Teil 2:"]
                for v in vocab:
                    v_lines.append(f"{v.get('de', '')} - {v.get('en', '')}.")
                generate_openai_audio("\n".join(v_lines), os.path.join(audio_dir, f"{model_id}_sprachbausteine_2_vocab.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

            for q in sp2.get("questions", []):
                num = q.get("number")
                correct = str(q.get("correct_answer", "")).lower()
                explanation = q.get("explanation", "")
                word_de = words_pool.get(correct, "")

                sol_lines = [f"Lösung für Lücke {num}: Das passende Wort ist Buchstabe {correct.upper()}: {word_de}."]
                if explanation:
                    sol_lines.append(f"Erklärung: {explanation}")
                generate_openai_audio("\n\n".join(sol_lines), os.path.join(audio_dir, f"{model_id}_sprachbausteine_2_q{num}_solution.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

    # 3. HOERVERSTEHEN
    if run_hoerverstehen:
        h1 = data.get("hoerverstehen_teil_1", {})
        if h1:
            intro_speech = "Modul 3: Hörverstehen. Teil 1. Sie hören fünf kurze Texte. Sie hören jeden Text zweimal. Wählen Sie für die Aufgaben 41 bis 45 die richtige Lösung: Richtig oder Falsch."
            generate_openai_audio(intro_speech, os.path.join(audio_dir, f"{model_id}_hoerverstehen_1_intro.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

            for item in h1.get("items", []):
                num = item.get("number")
                speaker = item.get("speaker", f"Sprecher {num}")
                text_de = item.get("text", "")
                text_en = item.get("text_en", "")
                stmt_de = item.get("statement", "")
                stmt_en = item.get("statement_en", "")
                correct = item.get("correct_answer", True)
                explanation = item.get("explanation", "")
                vocab = item.get("vocabulary", [])

                if text_de:
                    generate_openai_audio(f"Aufgabe {num}. {speaker}:\n\n{text_de}", os.path.join(audio_dir, f"{model_id}_hoerverstehen_1_item_{num}_de.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
                if text_en:
                    generate_openai_audio(f"English translation for Listening Item {num}:\n\n{text_en}", os.path.join(audio_dir, f"{model_id}_hoerverstehen_1_item_{num}_en.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
                if stmt_de:
                    st_text = f"Aussage zu Aufgabe {num}: {stmt_de}."
                    if stmt_en:
                        st_text += f" In English: {stmt_en}."
                    generate_openai_audio(st_text, os.path.join(audio_dir, f"{model_id}_hoerverstehen_1_item_{num}_statement.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
                if vocab:
                    v_lines = [f"Key vocabulary for Listening Item {num}:"]
                    for v in vocab:
                        v_lines.append(f"{v.get('de', '')} - {v.get('en', '')}.")
                    generate_openai_audio("\n".join(v_lines), os.path.join(audio_dir, f"{model_id}_hoerverstehen_1_item_{num}_vocab.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

                ans_word = "Richtig" if correct else "Falsch"
                sol_lines = [f"Lösung für Aufgabe {num}: Die Aussage ist {ans_word}."]
                if explanation:
                    sol_lines.append(f"Erklärung: {explanation}")
                generate_openai_audio("\n\n".join(sol_lines), os.path.join(audio_dir, f"{model_id}_hoerverstehen_1_item_{num}_solution.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

        h2 = data.get("hoerverstehen_teil_2", {})
        if h2:
            title = h2.get("title", "")
            intro = h2.get("intro", "")
            text_de = h2.get("text", "")
            text_en = h2.get("text_en", "")
            vocab = h2.get("vocabulary", [])

            generate_openai_audio(f"Modul 3: Hörverstehen. Teil 2. {title}. {intro}", os.path.join(audio_dir, f"{model_id}_hoerverstehen_2_intro.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
            if text_de:
                generate_openai_audio(text_de, os.path.join(audio_dir, f"{model_id}_hoerverstehen_2_full_de.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
            if text_en:
                generate_openai_audio(text_en, os.path.join(audio_dir, f"{model_id}_hoerverstehen_2_full_en.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
            if vocab:
                v_lines = ["Key vocabulary for Hörverstehen Teil 2:"]
                for v in vocab:
                    v_lines.append(f"{v.get('de', '')} - {v.get('en', '')}.")
                generate_openai_audio("\n".join(v_lines), os.path.join(audio_dir, f"{model_id}_hoerverstehen_2_vocab.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

            for q in h2.get("questions", []):
                num = q.get("number")
                stmt_de = q.get("statement", "")
                stmt_en = q.get("statement_en", "")
                correct = q.get("correct_answer", True)
                explanation = q.get("explanation", "")

                q_speech = f"Aufgabe {num}: {stmt_de}."
                if stmt_en:
                    q_speech += f" In English: {stmt_en}."
                generate_openai_audio(q_speech, os.path.join(audio_dir, f"{model_id}_hoerverstehen_2_q{num}.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

                ans_word = "Richtig" if correct else "Falsch"
                sol_lines = [f"Lösung für Aufgabe {num}: Die Aussage ist {ans_word}."]
                if explanation:
                    sol_lines.append(f"Erklärung: {explanation}")
                generate_openai_audio("\n\n".join(sol_lines), os.path.join(audio_dir, f"{model_id}_hoerverstehen_2_q{num}_solution.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

        h3 = data.get("hoerverstehen_teil_3", {})
        if h3:
            intro_speech = "Modul 3: Hörverstehen. Teil 3. Sie hören fünf kurze Gespräche. Sie hören jeden Text einmal. Wählen Sie für die Aufgaben 56 bis 60 die richtige Lösung: Richtig oder Falsch."
            generate_openai_audio(intro_speech, os.path.join(audio_dir, f"{model_id}_hoerverstehen_3_intro.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

            for item in h3.get("items", []):
                num = item.get("number")
                situation_de = item.get("situation", "")
                situation_en = item.get("situation_en", "")
                text_de = item.get("text", "")
                text_en = item.get("text_en", "")
                stmt_de = item.get("statement", "")
                stmt_en = item.get("statement_en", "")
                correct = item.get("correct_answer", True)
                explanation = item.get("explanation", "")
                vocab = item.get("vocabulary", [])

                if text_de:
                    generate_openai_audio(f"Aufgabe {num}. Situation: {situation_de}\n\n{text_de}", os.path.join(audio_dir, f"{model_id}_hoerverstehen_3_item_{num}_de.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
                if text_en:
                    generate_openai_audio(f"English translation for Task {num}. Context: {situation_en}\n\n{text_en}", os.path.join(audio_dir, f"{model_id}_hoerverstehen_3_item_{num}_en.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
                if stmt_de:
                    st_text = f"Aussage zu Aufgabe {num}: {stmt_de}."
                    if stmt_en:
                        st_text += f" In English: {stmt_en}."
                    generate_openai_audio(st_text, os.path.join(audio_dir, f"{model_id}_hoerverstehen_3_item_{num}_statement.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)
                if vocab:
                    v_lines = [f"Key vocabulary for Task {num}:"]
                    for v in vocab:
                        v_lines.append(f"{v.get('de', '')} - {v.get('en', '')}.")
                    generate_openai_audio("\n".join(v_lines), os.path.join(audio_dir, f"{model_id}_hoerverstehen_3_item_{num}_vocab.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

                ans_word = "Richtig" if correct else "Falsch"
                sol_lines = [f"Lösung für Aufgabe {num}: Die Aussage ist {ans_word}."]
                if explanation:
                    sol_lines.append(f"Erklärung: {explanation}")
                generate_openai_audio("\n\n".join(sol_lines), os.path.join(audio_dir, f"{model_id}_hoerverstehen_3_item_{num}_solution.mp3"), api_key, voice=voice, model=tts_model, overwrite=overwrite, delay=delay)

def sync_manifest():
    models = get_available_models()
    if not models:
        return

    manifest_data = {
        "title": "TELC Deutsch B1 Übungstests Manifest",
        "description": "Registry of all interactive TELC B1 practice test models and generated audio status.",
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "models": []
    }

    total_audio_files = 0
    for m in models:
        model_id = m["id"]
        model_audio_count = 0
        if os.path.exists(AUDIO_DIR):
            for f in os.listdir(AUDIO_DIR):
                if f.startswith(f"{model_id}_") and f.endswith(".mp3"):
                    model_audio_count += 1
        total_audio_files += model_audio_count

        manifest_data["models"].append({
            "id": model_id,
            "filename": m["file"],
            "title": m["title"],
            "description": m["description"],
            "audio_count": model_audio_count,
            "has_audio": model_audio_count > 0
        })

    manifest_data["total_models"] = len(models)
    manifest_data["total_audio_files"] = total_audio_files

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    print(f"\n[Manifest Updated] {MANIFEST_PATH} ({len(models)} models, {total_audio_files} total audio files)")

def main():
    parser = argparse.ArgumentParser(
        description="Generate high-quality German & English AI audio for TELC B1 study models via OpenAI TTS API."
    )
    parser.add_argument(
        "--model", "--test",
        default="all",
        help="Target test model ID (e.g. 'eva1', 'petra', 'sophie', 'eva1,petra', or 'all'). Default: 'all'"
    )
    parser.add_argument(
        "--section",
        default="all",
        choices=["all", "hoerverstehen", "leseverstehen", "sprachbausteine"],
        help="Filter generation by test module/section. Default: 'all'"
    )
    parser.add_argument(
        "--voice",
        default="alloy",
        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        help="OpenAI TTS voice to use. Default: 'alloy'"
    )
    parser.add_argument(
        "--tts-model",
        default="tts-1",
        choices=["tts-1", "tts-1-hd"],
        help="OpenAI TTS model. Default: 'tts-1'"
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("OPENAI_API_KEY", ""),
        help="OpenAI API Key (or set OPENAI_API_KEY environment variable)."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate and overwrite existing MP3 audio files."
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.05,
        help="Delay between API requests in seconds. Default: 0.05s"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List all discovered test model files in data/ and exit."
    )
    parser.add_argument(
        "--sync-manifest-only",
        action="store_true",
        help="Synchronize manifest_models.json without generating audio."
    )

    args = parser.parse_args()

    if args.list_models:
        avail = get_available_models()
        print("\n=======================================================")
        print("Discovered TELC B1 Test Models in data/:")
        print("=======================================================")
        for m in avail:
            print(f"  • ID: {m['id']:<10} | File: {m['file']:<16} | Title: {m['title']}")
        print(f"\nTotal models: {len(avail)}")
        return

    if args.sync_manifest_only:
        sync_manifest()
        return

    if not args.api_key:
        print("\n[Error] OpenAI API Key is required!")
        print("Please supply it via:")
        print("  1. Environment variable: export OPENAI_API_KEY='sk-...'")
        print("  2. CLI argument:         python3 scripts/generate_ai_audio.py --api-key 'sk-...'")
        print("  3. GitHub Action Secret: OPENAI_API_KEY")
        sys.exit(1)

    avail_models = get_available_models()
    avail_ids = {m["id"]: m["path"] for m in avail_models}

    target_arg = args.model.strip().lower()
    selected_paths = []

    if target_arg == "all":
        selected_paths = [m["path"] for m in avail_models]
    else:
        requested_ids = [x.strip() for x in target_arg.split(",") if x.strip()]
        for req_id in requested_ids:
            if req_id in avail_ids:
                selected_paths.append(avail_ids[req_id])
            else:
                print(f"[Warning] Model ID '{req_id}' not found in data/. Available: {list(avail_ids.keys())}")

    if not selected_paths:
        print("[Error] No valid test model found to process.")
        sys.exit(1)

    print(f"\nStarting AI Audio Generation:")
    print(f"  • Models:    {[os.path.splitext(os.path.basename(p))[0] for p in selected_paths]}")
    print(f"  • Section:   {args.section}")
    print(f"  • Voice:     {args.voice} ({args.tts_model})")
    print(f"  • Overwrite: {args.overwrite}")

    os.makedirs(AUDIO_DIR, exist_ok=True)

    start_time = time.time()
    for path in selected_paths:
        process_model_file(
            model_path=path,
            audio_dir=AUDIO_DIR,
            api_key=args.api_key,
            voice=args.voice,
            tts_model=args.tts_model,
            overwrite=args.overwrite,
            section=args.section,
            delay=args.delay
        )

    sync_manifest()

    elapsed = time.time() - start_time
    print("\n" + "=" * 55)
    print("AI Audio Generation Complete!")
    print(f"  • Newly Generated: {stats['generated']}")
    print(f"  • Skipped Existing:{stats['skipped']}")
    print(f"  • Failed/Errors:   {stats['failed']}")
    print(f"  • Elapsed Time:    {elapsed:.1f}s")
    print("=" * 55)

if __name__ == "__main__":
    main()
