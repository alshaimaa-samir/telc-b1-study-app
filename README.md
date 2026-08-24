# 🇩🇪 telc Deutsch B1 Test Trainer & Audio Study App

A lightweight, zero-dependency, mobile-first **Progressive Web App (PWA)** built for mastering the official **telc Deutsch B1 Zertifikat** examination.

Designed for seamless offline study on **iPhone, iPad, Android, and Desktop**.

---

## 🌟 Core Features

### 1. 📚 Complete 8-Part Exam Modules (60 Questions per Test)
* **📖 Module 1: Leseverstehen (Reading • 75.0 Pkt Total)**
  * **Teil 1 (Zuordnung • 1–5):** 5 texts matched to 10 headings (*5.0 Pkt each • 25 Pkt*).
  * **Teil 2 (Artikel • 6–10):** Full newspaper article with 3-choice questions (*5.0 Pkt each • 25 Pkt*).
  * **Teil 3 (Anzeigen • 11–20):** 10 situations matched to 12 classified ads or 'x' (*2.5 Pkt each • 25 Pkt*).
* **✍️ Module 2: Sprachbausteine (Grammar & Vocabulary • 30.0 Pkt Total)**
  * **Teil 1 (Brief Cloze • 21–30):** Formal letter with 3 grammatical choices (*1.5 Pkt each • 15 Pkt*).
  * **Teil 2 (Wortkasten • 31–40):** Article with 15-word vocabulary bank (*1.5 Pkt each • 15 Pkt*).
* **🎧 Module 3: Hörverstehen (Listening • 75.0 Pkt Total)**
  * **Teil 1 (Ansagen • 41–45):** 5 public announcements with True/False (*3.75 Pkt each • 18.75 Pkt*).
  * **Teil 2 (Interview • 46–55):** Long-form radio interview with True/False (*3.75 Pkt each • 37.5 Pkt*).
  * **Teil 3 (Gespräche • 56–60):** 5 everyday conversations with True/False (*3.75 Pkt each • 18.75 Pkt*).

---

### 2. 🎯 Official telc B1 Scoring & Grade System
* **Written Test Max:** **225.0 Points** (180.0 auto-graded base + 45.0 writing).
* **Passing Mark:** **60% (135.0 Points)** for the written test; **45.0 Points** for the oral test.
* **Official Grade Calculation:**
  * **Sehr gut (1):** 270.0 – 300.0 Pkt (90% – 100%)
  * **Gut (2):** 240.0 – 269.5 Pkt (80% – 89%)
  * **Befriedigend (3):** 210.0 – 239.5 Pkt (70% – 79%)
  * **Ausreichend (4):** 180.0 – 209.5 Pkt (60% – 69%)
  * **Nicht bestanden:** < 180.0 Pkt (< 60%)
* **Interactive Scoring Guide Modal:** 1-click modal with full breakdown tables.

---

### 3. 🛠️ Study Tools & Ergonomics
* **✨ "Answer Test For Me":** 1-click auto-solver for rapid test verification and answer key inspection.
* **🔄 Per-Question Reset:** Discrete inline `🔄` icon at the end of each question to clear individual answers with an instant `Reset Answer` tooltip.
* **🔁 Test Reset & Clear All:** Repeat icon beside each test title to reset individual models or clear all progress.
* **⭐ Fehlerheft (Mistakes Notebook):** Star difficult questions to filter and review later.
* **🔍 Focus Reader Modal:** Clean modal reader for passages with native text-to-speech listening.
* **🌐 English Subtitles Toggle:** Instant toggle for German $\leftrightarrow$ English translations.
* **📻 Podcast / Background Audio Mode:** Continuous hands-free audio listening with MediaSession lockscreen controls.
* **📱 Responsive Layouts:**
  * **Desktop / iPad:** Collapsible 60-width sidebar / 48px slim icon rail.
  * **Mobile Phones:** Sticky bottom navigation bar with 1-tap pop-up bottom sheet index.

---

## 🚀 Running Locally

```bash
cd /usr/local/google/home/alshaimaa/telc-study-app
python3 -m http.server 8080
```
Open **`http://localhost:8080`** in your browser.

---

## 📱 Mobile & iPad Deployment Guide (PWA)

### Option 1: Deploy to GitHub Pages (Free & Recommended)
1. Initialize git and commit:
   ```bash
   cd /usr/local/google/home/alshaimaa/telc-study-app
   git init
   git add .
   git commit -m "Deploy telc Deutsch B1 Study App"
   ```
2. Create and push to a GitHub repository:
   ```bash
   gh repo create telc-b1-study-app --public --source=. --push
   ```
3. In GitHub repo settings $ightarrow$ **Pages** $ightarrow$ Source: `Deploy from branch` (`main` / root).
4. Open the generated `https://<username>.github.io/telc-b1-study-app/` URL on your phone or iPad.

---

### Option 2: Deploy to Cloudflare Pages / Vercel (1-Click Free Hosting)
1. Push to GitHub or connect the directory.
2. Build command: *(leave empty / static)*, Output directory: `./`.
3. Your app is live with free SSL and instant global CDN!

---

### 📲 Installing on iPhone / iPad / Android Home Screen
* **iOS / iPadOS (Safari):**
  1. Open the deployed web app URL in Safari.
  2. Tap the **Share** button (`⎋` or square with up arrow).
  3. Scroll down and tap **Add to Home Screen** (`➕`).
  4. The app will launch in full-screen standalone mode and work offline!
* **Android (Chrome):**
  1. Open the URL in Chrome.
  2. Tap the 3 dots menu (`⋮`) $ightarrow$ **Install App** / **Add to Home screen**.
