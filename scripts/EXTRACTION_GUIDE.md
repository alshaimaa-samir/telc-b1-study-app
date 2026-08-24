# TELC B1 EXAM DATA EXTRACTION GUIDE & JSON SPECIFICATION

When adding a new practice test (`model_03.json` ... `model_26.json`), extract the text and solutions into the canonical JSON structure defined below.

## Complete Template (`data/schema_telc_b1.json`)

```json
{
  "title": "Übungstest X",
  
  "leseverstehen_teil_1": {
    "headings": {
      "a": "Heading A...",
      "b": "Heading B...",
      "c": "...", "d": "...", "e": "...", "f": "...", "g": "...", "h": "...", "i": "...", "j": "..."
    },
    "headings_en": {
      "a": "Translation A...", "b": "..."
    },
    "passages": [
      {
        "number": 1,
        "text": "German text of passage 1...",
        "text_en": "English translation...",
        "correct_answer": "b",
        "explanation": "Why b is correct...",
        "vocabulary": [
          {"de": "Wort", "en": "word"}
        ]
      }
    ]
  },

  "leseverstehen_teil_2": {
    "passage": {
      "headline": "Article Headline",
      "subheadline": "Subheadline",
      "paragraphs": [
        "Paragraph 1...",
        "Paragraph 2..."
      ],
      "text_en": "English translation...",
      "vocabulary": []
    },
    "questions": [
      {
        "number": 6,
        "question": "Question text...",
        "question_en": "English question...",
        "options": {
          "a": "Option A",
          "b": "Option B",
          "c": "Option C"
        },
        "options_en": {
          "a": "...", "b": "...", "c": "..."
        },
        "correct_answer": "b",
        "explanation": "Explanation..."
      }
    ]
  },

  "leseverstehen_teil_3": {
    "advertisements": {
      "a": {
        "title": "Ad Title",
        "subtitle": "Ad Subtitle",
        "lines": ["Line 1", "Line 2"],
        "image": "data/images/model_ad_a.png",
        "text_en": "Translation...",
        "vocabulary": []
      }
    },
    "situations": [
      {
        "number": 11,
        "situation": "Situation description...",
        "situation_en": "Translation...",
        "correct_answer": "g",
        "explanation": "Explanation..."
      }
    ]
  },

  "sprachbausteine_teil_1": {
    "instructions": "Lesen sie den Text und schließen Sie Lücken 21-30.",
    "passage": {
      "text": "Sehr geehrte Damen und Herren,\n\nich schreibe Ihnen wegen ___21___ Wohnung...",
      "text_en": "Dear Sir or Madam,\n\nI am writing regarding ___21___ apartment...",
      "vocabulary": []
    },
    "questions": [
      {
        "number": 21,
        "options": {"a": "ihr", "b": "ihrem", "c": "ihren"},
        "correct_answer": "b",
        "explanation": "Dativ maskulin/neutral..."
      }
    ]
  },

  "sprachbausteine_teil_2": {
    "instructions": "Lesen sie den Text und schließen Sie Lücken 31-40. Benutzen Sie die Wörter (a - o).",
    "word_bank": {
      "a": "am", "b": "bis", "c": "dass", "d": "für", "e": "gute",
      "f": "keine", "g": "mich", "h": "mir", "i": "mit", "j": "möchte",
      "k": "ohne", "l": "pro", "m": "während", "n": "wäre", "o": "würden"
    },
    "word_bank_en": {
      "a": "at the", "b": "until"
    },
    "passage": {
      "headline": "Passage Headline",
      "text": "Text with blanks ___31___ through ___40___...",
      "text_en": "Translation...",
      "vocabulary": []
    },
    "questions": [
      {
        "number": 31,
        "correct_answer": "h",
        "explanation": "Dativ..."
      }
    ]
  },

  "hoerverstehen_teil_1": {
    "instructions": "Sie hören nun fünf kurze Texte (41-45).",
    "transcripts": [
      {
        "number": 41,
        "text": "German audio transcript...",
        "text_en": "English transcript...",
        "vocabulary": []
      }
    ],
    "questions": [
      {
        "number": 41,
        "statement": "Statement to evaluate...",
        "statement_en": "English statement...",
        "correct_answer": "+",
        "explanation": "Why true (+)..."
      }
    ]
  },

  "hoerverstehen_teil_2": {
    "instructions": "Sie hören nun ein Gespräch (46-55).",
    "interview_transcript": {
      "text": "Moderator: ...\nGast: ...",
      "text_en": "Translation...",
      "vocabulary": []
    },
    "questions": [
      {
        "number": 46,
        "statement": "Statement...",
        "statement_en": "Translation...",
        "correct_answer": "-",
        "explanation": "Why false (-)..."
      }
    ]
  },

  "hoerverstehen_teil_3": {
    "instructions": "Sie hören nun fünf kurze Texte (56-60).",
    "transcripts": [
      {
        "number": 56,
        "text": "German audio dialogue transcript...",
        "text_en": "English transcript...",
        "vocabulary": []
      }
    ],
    "questions": [
      {
        "number": 56,
        "statement": "Statement...",
        "statement_en": "Translation...",
        "correct_answer": "+",
        "explanation": "Why true (+)..."
      }
    ]
  }
}
```

## Answer Conventions:
* **Headings (1–5):** lowercase `'a'` – `'j'`
* **Reading Multi-Choice (6–10):** lowercase `'a'`, `'b'`, `'c'`
* **Classified Ads (11–20):** lowercase `'a'` – `'l'` or `'x'`
* **Letter Cloze (21–30):** lowercase `'a'`, `'b'`, `'c'`
* **Word Bank (31–40):** lowercase `'a'` – `'o'`
* **Listening Statements (41–60):** `"+"` (Richtig) or `"-"` (Falsch)
