# TELC B1 STUDY TRACKER APP — ARCHITECTURE & SPECIFICATION

## 1. Overview
The **Telc Deutsch B1 Test Trainer** is a zero-build client-side Progressive Web Application (PWA) designed to practice complete 60-question **Telc Deutsch B1 Zertifikat** examinations.

---

## 2. Standard Exam Data Architecture (Canonical Schema)
All practice tests in `data/{model_id}.json` (e.g. `data/eva1.json`, `data/petra.json`, `data/sophie.json`) strictly follow the canonical **60-Question Telc B1 Schema**:

```json
{
  "title": "Petra",
  "leseverstehen_teil_1": { "headings": {}, "headings_en": {}, "passages": [] },
  "leseverstehen_teil_2": { "passage": {}, "questions": [] },
  "leseverstehen_teil_3": { "advertisements": {}, "situations": [] },
  "sprachbausteine_teil_1": { "letter": {}, "items": [] },
  "sprachbausteine_teil_2": { "word_bank": {}, "passage": {}, "items": [] },
  "hoerverstehen_teil_1": { "items": [] },
  "hoerverstehen_teil_2": { "interview_transcript": {}, "items": [] },
  "hoerverstehen_teil_3": { "items": [] }
}
```

---

## 3. Scoring & Points Structure (Official telc B1 Model)

| Module | Part | Items | Points Per Item | Total Points | Auto-Graded |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Leseverstehen** | Teil 1 (Zuordnung) | 1–5 (5 Qs) | 5.0 Pkt | 25.0 Pkt | Yes |
| | Teil 2 (Artikel) | 6–10 (5 Qs) | 5.0 Pkt | 25.0 Pkt | Yes |
| | Teil 3 (Anzeigen) | 11–20 (10 Qs) | 2.5 Pkt | 25.0 Pkt | Yes |
| **Sprachbausteine**| Teil 1 (Brief) | 21–30 (10 Qs)| 1.5 Pkt | 15.0 Pkt | Yes |
| | Teil 2 (Wortkasten)| 31–40 (10 Qs)| 1.5 Pkt | 15.0 Pkt | Yes |
| **Hörverstehen** | Teil 1 (Ansagen) | 41–45 (5 Qs) | 3.75 Pkt | 18.75 Pkt | Yes |
| | Teil 2 (Interview) | 46–55 (10 Qs)| 3.75 Pkt | 37.5 Pkt | Yes |
| | Teil 3 (Gespräche) | 56–60 (5 Qs) | 3.75 Pkt | 18.75 Pkt | Yes |
| **Schriftlicher Ausdruck** | Brief schreiben | — | — | 45.0 Pkt | Manual/Writing |
| **Mündliche Prüfung** | Sprechen 1–3 | — | — | 75.0 Pkt | Oral Exam |
| **TOTAL** | | **60 Qs** | | **300.0 Pkt** | |

* **Written Test Total:** **225.0 Points** (180.0 Auto-Graded + 45.0 Writing).
* **Passing Mark:** $\ge 60\%$ (135.0 Points for written; 45.0 Points for oral).

---

## 4. Key JavaScript Subsystems in `index.html`

1. **State & Local Persistence:**
   * `userState`: `{ answers: { [qKey]: value }, flagged: { [qKey]: boolean } }`
   * Key Format: `${modelId}_${sectionId}_${qNum}` (e.g. `petra_teil_1_1`, `eva1_hoerverstehen_2_46`).
   * Sanitization on boot purges empty or orphaned keys.

2. **Universal Answer Extraction:**
   * `extractCorrectAnswersFromModel(mData)` parses `questions`, `items`, `passages`, and `situations` across all 8 parts.

3. **Answer Automation & Reset:**
   * `autoAnswerCurrentTest()` fills all 60 answers with official solutions.
   * `clearSingleAnswer(qKey)` clears a specific question.
   * `resetTestPrompt(modelId)` resets a single test model.
   * `resetAllProgressPrompt()` wipes all progress.

4. **Speech & Audio Mode:**
   * SpeechSynthesis API for sentence-by-sentence listening and podcast loop mode.
   * MediaSession API for lockscreen audio playback control.

5. **PWA & Offline Support:**
   * `sw.js` caches all core files and JSON test assets for 100% offline capability.
