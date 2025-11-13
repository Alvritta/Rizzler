# Backend - Rizz Calculator API

FastAPI backend for the Rizz Calculator MVP using Gemini 2.5 Flash Vision API.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your Supabase and Gemini API credentials:
     ```
     SUPABASE_URL=your_supabase_project_url
     SUPABASE_ANON_KEY=your_supabase_anon_key
     GEMINI_API_KEY=your_gemini_api_key
     ```

3. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```
   
   Or:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Health check
- `POST /auth/signup/` - Sign up new user (email, password)
- `POST /auth/login/` - Login user (email, password)
- `POST /calculate-rizz/` - Upload image and get rizz score (requires auth)
- `GET /leaderboard/` - Get top 10 users by average rizz score
- `GET /user/scores/` - Get all scores for current user (requires auth)

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notes

- Uses Gemini 2.5 Flash Vision API for direct image analysis (no OCR needed)
- Images are stored in Supabase Storage bucket `chat-images`
- Scores are stored in Supabase `scores` table
- Authentication uses Supabase JWT tokens

