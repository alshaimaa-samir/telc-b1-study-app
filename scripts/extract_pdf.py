#!/usr/bin/env python3
"""
Telc B1 Exam PDF Extractor & Structurer
Extracts Leseverstehen (Teil 1, 2, 3) from Telc B1 exam PDFs into the app JSON format.
"""

import json
import os
import sys

SAMPLE_SCHEMA = {
    "id": "model_02",
    "title": "Telc B1 - Modelltest 2",
    "description": "Leseverstehen Teil 1, 2 und 3",
    "sections": {
        "teil_1": {
            "id": "teil_1",
            "title": "Leseverstehen - Teil 1 (Texte & Überschriften)",
            "instructions": "Lesen Sie die Überschriften a–j und die Texte 1–5.",
            "headings": {
                "a": "Überschrift A",
                "b": "Überschrift B"
            },
            "headings_en": {
                "a": "Heading A in English",
                "b": "Heading B in English"
            },
            "passages": [
                {
                    "number": 1,
                    "title": "Text 1",
                    "text": "Deutscher Text...",
                    "text_en": "English translation...",
                    "correct_answer": "a",
                    "clues": "Key matching clues...",
                    "explanation": "German explanation..."
                }
            ]
        },
        "teil_2": {
            "id": "teil_2",
            "title": "Leseverstehen - Teil 2 (Zeitungsartikel)",
            "instructions": "Lesen Sie den folgenden Text und die Aufgaben 6–10.",
            "passage": {
                "title": "Titel des Artikels",
                "text": "Deutscher Artikel...",
                "text_en": "English article translation..."
            },
            "questions": [
                {
                    "number": 6,
                    "question": "Frage 6...",
                    "question_en": "Question 6 in English...",
                    "options": {
                        "a": "Option A",
                        "b": "Option B",
                        "c": "Option C"
                    },
                    "options_en": {
                        "a": "Option A in English",
                        "b": "Option B in English",
                        "c": "Option C in English"
                    },
                    "correct_answer": "b",
                    "explanation": "Erklärung warum B richtig ist..."
                }
            ]
        },
        "teil_3": {
            "id": "teil_3",
            "title": "Leseverstehen - Teil 3 (Situationen & Anzeigen)",
            "instructions": "Lesen Sie die Situationen 11–20 und die Anzeigen a–l.",
            "advertisements": {
                "a": {
                    "title": "Anzeige A: Titel",
                    "text": "Anzeigentext...",
                    "text_en": "Advertisement text in English..."
                }
            },
            "situations": [
                {
                    "number": 11,
                    "situation": "Situation auf Deutsch...",
                    "situation_en": "Situation in English...",
                    "correct_answer": "a",
                    "explanation": "Erklärung..."
                }
            ]
        }
    }
}

def main():
    print("Telc B1 Exam PDF Ingestion Helper")
    print("=================================")
    print("To add new exams, place your extracted JSON files into data/ (e.g., data/model_02.json).")
    print(f"Data directory: {os.path.abspath('../data')}")

if __name__ == "__main__":
    main()
