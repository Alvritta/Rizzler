# Backend - Rizz Calculator API

FastAPI backend for the Rizz Calculator MVP using Gemini 2.5 Flash Vision API.

## Setup

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Create a `.env` file in the `backend/` directory
   - Add your Supabase and Gemini API credentials:
     ```
     SUPABASE_URL=your_supabase_project_url
     SUPABASE_ANON_KEY=your_supabase_anon_key
     GEMINI_API_KEY=your_gemini_api_key
     PORT=8000
     ```
   - **Important:** Never commit the `.env` file to git (it's in .gitignore)

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
- `POST /auth/login/` - Login user (email, password) - **Returns access_token**
- `POST /calculate-rizz/` - Upload image and get rizz score (requires auth)
- `GET /leaderboard/` - Get top 10 users by average rizz score
- `GET /user/scores/` - Get all scores for current user (requires auth)

## Authentication Flow

1. **Login to get access token:**
   ```bash
   POST /auth/login/
   Content-Type: application/json
   
   {
     "email": "your@email.com",
     "password": "yourpassword"
   }
   ```
   
   Response:
   ```json
   {
     "message": "Login successful",
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "user": {...}
   }
   ```

2. **Use the access_token in Authorization header:**
   ```bash
   POST /calculate-rizz/
   Authorization: Bearer <access_token_from_login>
   Content-Type: multipart/form-data
   
   file: <image_file>
   ```

## Example Usage

See `test_auth.py` for a complete example of:
- Getting an access token from login
- Using it to call protected endpoints

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notes

- Uses Gemini 2.5 Flash Vision API for direct image analysis (no OCR needed)
- Images are stored in Supabase Storage bucket `chat-images`
- Scores are stored in Supabase `scores` table
- Authentication uses Supabase JWT tokens

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your actual environment variables (create this)
└── README.md            # This file
```

