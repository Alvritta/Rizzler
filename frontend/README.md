# Frontend - Rizz Calculator

Simple HTML/JS frontend for the Rizz Calculator MVP.

## Setup

1. **Update configuration in `index.html`:**
   - Open `index.html` in a text editor
   - Find the configuration section (around line 200) and update:
     ```javascript
     const SUPABASE_URL = 'YOUR_SUPABASE_URL';
     const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';
     const BACKEND_URL = 'http://localhost:8000'; // Change to deployed URL
     ```

2. **Serve the frontend:**
   
   **Option 1: Simple HTTP Server (Python)**
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Then open `http://localhost:8080` in your browser.
   
   **Option 2: Simple HTTP Server (Node.js)**
   ```bash
   cd frontend
   npx http-server -p 8080
   ```
   
   **Option 3: Open directly**
   - Just open `index.html` in your browser (may have CORS issues with API calls)

## Features

- User authentication (signup/login) via Supabase
- Image upload with drag & drop support
- Image preview before upload
- Rizz score calculation with Gemini Vision API
- Display of score, reasoning, and suggestions
- Leaderboard showing top 10 users
- Responsive design

## Notes

- Make sure your backend is running and accessible
- Update `BACKEND_URL` when deploying to production
- The frontend uses Supabase JS client from CDN (no build step needed)

