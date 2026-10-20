# ⚡ SMSHARE — Neo-Brutalism Privacy-First Sharing Platform

A 100% working, full-featured temporary file and text sharing platform built with a high-contrast **Neo-Brutalism** design system.

No logins, no signups, no tracking cookies, and zero permanent storage. Drop a message or upload files, get a 4-character code, and share it. Everything self-destructs after expiry.

---

## 🚀 Quick Start (Single Command)

To launch the server and automatically open your default browser:

```bash
py run.py
```

Or double-click `start_server.bat` in Windows File Explorer.

You can also run directly with Uvicorn:

```bash
py -m uvicorn server:app --host 0.0.0.0 --port 8000
```

Open your browser at: **`http://localhost:8000`**

---

## 🎨 Neo-Brutalism Design Features

- **Thick Stark Borders**: `3px` solid black borders across all interactive cards and elements.
- **Hard Unblurred Drop Shadows**: High-contrast `5px 5px 0px #000000` retro shadows.
- **Tactile Button Press States**: Translates diagonally on click with real tactile resistance.
- **Vibrant Accent Palette**: Electric Yellow (`#FFE600`), Cyber Cyan (`#00F0FF`), Neon Pink (`#FF5C8A`), Ultra Lime (`#52FF00`), and Lilac (`#B388FF`).
- **Dark / Light Cyber-Brutalist Mode**: Seamless theme toggle with state persisted in `localStorage`.
- **Dynamic Monospace Code Display**: High-visibility 4-character code display with instant copy buttons and embedded mobile QR code.

---

## 🛠️ Complete Feature Set

### 1. Send Mode 🚀
- **Unified Text Area**: Paste text, URLs, notes, or code snippets with `⌘↵` / `Ctrl+Enter` shortcut.
- **Multi-File Drag & Drop**: Upload up to **10 files** at once (up to **500 MB each**).
- **File Chips**: Live file size calculation, file icons (images, audio, video, PDFs, archives, code), and individual delete buttons.
- **Configurable Auto-Destruct Timer**:
  - `30 Minutes` (Default)
  - `2 Hours`
  - `12 Hours`
  - `24 Hours`
- **Live Upload Progress**: Striped Neo-Brutalism progress bar with real-time percentage tracking.
- **Instant Result Screen**:
  - Giant 4-character code (e.g. `QLDK`) in monospace styling.
  - "Copy Code" button with toast notification.
  - "Copy Direct Link" button (`http://localhost:8000/?code=QLDK`).
  - Embedded SVG QR Code for instant phone camera scanning.
  - Live client-side countdown timer showing real-time remaining minutes & seconds.

### 2. Receive Mode 📥
- **4-Character Code Input**: Auto-capitalizing input with auto-retrieval upon typing 4 characters.
- **Direct Link Support**: Visiting `http://localhost:8000/?code=XXXX` or `http://localhost:8000/c/XXXX` immediately switches to Receive mode and retrieves content.
- **Verified Content View**:
  - Live auto-destruct countdown timer.
  - Text payload card with one-click "Copy Text" button.
  - File cards with individual "Download" buttons.
  - **Inline Media Previews**: Instant previews for images (`.png`, `.jpg`, `.webp`, `.gif`), audio (`.mp3`, `.wav`), and video (`.mp4`, `.webm`).
  - **📦 Download All as ZIP**: Streams a compressed `.zip` archive containing all uploaded files plus a transfer receipt.

### 3. Privacy & Zero-Retention Engine 🔒
- **Zero Identity**: No accounts, emails, phone numbers, or IP logging.
- **Background Purge Worker**: Asynchronous background loop runs every 20 seconds, querying expired database records and hard-deleting associated files from disk (`uploads/{code}/`).
- **On-Access Purge**: If an expired share is requested before the periodic loop runs, it is immediately deleted and returns a 404.

### 4. Interactive Sections & Modals
- **"How it works"**: 4-step Neo-Brutalist cards (01 Compose, 02 Get a code, 03 Share the code, 04 Auto-wipe).
- **"Built for privacy-first sharing"**: Core guarantees feature matrix.
- **Interactive FAQ Accordion**: Expandable/collapsible answers matching official Q&As.
- **Working Modals**: About, Privacy Policy, Terms of Service, and Contact modal with toast confirmation.

---

## 🧪 Automated Test Suite

A complete verification script is included:

```bash
py test_smshare.py
```

Tests cover:
- System health and configuration limits.
- Text payload transmission and retrieval.
- Multi-file uploads, individual file downloads, and ZIP bundle verification.
- Database hard-deletion and disk wipe on expiry.
- Static file serving (HTML, CSS, JS).

---

## 📂 Project Architecture

```
d:\FILE SHARESS\
├── server.py             # FastAPI backend with REST endpoints, file streaming & zip generation
├── database.py           # SQLite WAL metadata store & 4-char code generation
├── run.py                # Single-command runner with browser launcher
├── start_server.bat      # Windows batch launcher
├── test_smshare.py       # Automated end-to-end verification test suite
├── static/
│   ├── index.html        # Complete Neo-Brutalism SPA frontend
│   ├── style.css         # Neo-Brutalism CSS design system (Light & Dark themes)
│   ├── app.js            # Reactive client controller, QR generator & countdown timers
│   └── favicon.svg       # Neo-Brutalist icon
└── uploads/              # Temporary storage partition (auto-purged on expiry)
```
