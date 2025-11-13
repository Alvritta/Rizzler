# Quick Start Guide - Backend Server

## Start the Server

Before testing the API, you need to start the FastAPI server:

### Option 1: Using uvicorn (Recommended)
```bash
cd RC/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Using Python directly
```bash
cd RC/backend
python main.py
```

### Option 3: Using uvicorn with auto-reload (for development)
```bash
cd RC/backend
uvicorn main:app --reload
```

## Verify Server is Running

Once started, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Then test it:
```bash
curl http://localhost:8000/
```

Should return:
```json
{"message": "Rizz Calculator API", "status": "running"}
```

## Common Issues

### Port Already in Use
If port 8000 is already in use:
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or use a different port
uvicorn main:app --reload --port 8001
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Missing .env file
Create `.env` file in `backend/` directory with:
```
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key
GEMINI_API_KEY=your_key
```

## Testing After Server Starts

Once the server is running, you can test:

```bash
# Test login
python test_auth_header.py your@email.com password image.jpg
```

Or use curl:
```bash
# Login
curl -X POST "http://localhost:8000/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"password"}'
```


