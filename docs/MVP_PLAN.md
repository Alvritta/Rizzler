# Quick MVP Plan: Rizz Calculator Web App (Using Supabase & Free Tools)

This document outlines building a minimal viable product (MVP) for your rizz calculator app using **free tools only**: Supabase (DB + storage + auth), FastAPI (backend), a simple HTML/JS frontend, and Gemini 2.5 Flash Vision API (free tier for LLM-based rizz scoring). Total build time: ~4-6 hours for a solo dev or AI agent. Focus: Core flow (upload → score + suggestions → leaderboard), no fancy UI/polish.

**Assumptions**:
- Users sign up/login via Supabase Auth (email or Google).
- Rizz calc: Gemini Vision API analyzes chat screenshot → LLM prompts for score (0-100) + 3 suggestions.
- Leaderboard: Top 10 avg scores.
- Free limits: Supabase (500MB DB, 1GB storage), Gemini (60 queries/min, 1M tokens/day), Render (750 free hours/month).

## 1. Project Setup (15-30 min)
- **Tools & Repo**:
  - Create GitHub repo: `rizz-calculator-mvp`.
  - Folders: `/backend` (FastAPI), `/frontend` (static HTML/JS), `/docs` (this plan).
  - Install locally: Python 3.10+, Node.js (optional for frontend bundling).
  - Free accounts: Supabase (project), Google AI Studio (Gemini API key), Render (account).
- **Env Setup**:
  - `.env` file (gitignore it): `SUPABASE_URL=...`, `SUPABASE_ANON_KEY=...`, `GEMINI_API_KEY=...`.
  - Requirements (`backend/requirements.txt`): 
    ```
    fastapi[all]
    uvicorn
    supabase
    google-generativeai
    python-dotenv
    python-multipart
    ```

## 2. Supabase Setup (20-30 min)
- Create project at [supabase.com](https://supabase.com) (free tier).
- **Auth**: Enable Email + Google providers in Auth settings.
- **Storage**: Create bucket `chat-images` (public read, private write via policies).
- **Database Schema**: See `SUPABASE_SETUP.md` for full SQL schema.

## 3. Backend: FastAPI Implementation (1-2 hours)
- File: `backend/main.py`.
- Core Endpoints:
  - `/auth/signup`, `/auth/login`: Use Supabase Auth helpers (implement basic JWT dependency).
  - `/calculate-rizz`: POST image → Gemini Vision API → Store → Return score/suggestions.
  - `/leaderboard`: GET top 10.
- Uses Gemini 2.5 Flash Vision API for direct image analysis (no OCR needed).

## 4. Frontend: Simple HTML/JS (30-45 min)
- File: `frontend/index.html` (single page, no framework for speed).
- Features: Login form, upload button, display score/suggestions, leaderboard table.
- Use Supabase JS client (`<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>`).

## 5. Integration & Testing (30 min)
- **Local Run**: `cd backend && uvicorn main:app --reload`. Open `frontend/index.html` in browser (serve via `python -m http.server` if CORS issues).
- **Test Flow**: Signup → Upload sample chat screenshot → Verify score in Supabase dashboard → Check leaderboard.
- **Edge Cases**: Bad image (fallback score), auth errors (401 redirect to login).
- **Security**: RLS policies prevent unauthorized inserts; validate uploads (size <5MB via FastAPI).

## 6. Deployment (15-20 min)
- **Backend**: [Render.com](https://render.com) (free web service).
  - Connect GitHub repo → Select `/backend` → Build: `pip install -r requirements.txt` → Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
  - Add env vars in Render dashboard (Supabase + Gemini keys).
- **Frontend**: Render Static Site (same repo, `/frontend`) or [Netlify](https://netlify.com) (drag-drop folder, free).
- **Full URL**: Backend at `https://your-app.onrender.com`, frontend points to it.
- **Supabase**: Update policies if needed for public access.

## 7. Next Steps & Polish (Post-MVP)
- **Metrics**: Add Supabase analytics or free Google Analytics.
- **Improvements**: Better UI (Bootstrap CDN), mobile responsiveness, more LLM prompts.
- **Share with Codex Agent**: Paste this MD into the agent's prompt, include code skeletons, and say: "Implement this MVP plan step-by-step, outputting full code files."

This MVP validates the core idea—launch it, get feedback, iterate. Total cost: $0. If issues (e.g., Gemini API flakiness), fallback to rule-based scoring. Let's make rizz great again! 🚀

