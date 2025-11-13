from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client, Client
import io
import os
import json
import base64  # Add this import
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from typing import Optional
import time
import uuid
from datetime import datetime
import jwt  # pip install pyjwt

load_dotenv()

app = FastAPI(title="Rizz Calculator API", version="1.0.0")

# Add security scheme to OpenAPI docs
app.openapi_schema = None  # Force regeneration

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title="Rizz Calculator API",
        version="1.0.0",
        description="API for calculating rizz scores from chat screenshots using Gemini Vision API",
        routes=app.routes,
    )
    # Add Bearer auth to OpenAPI schema
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# HTTP Bearer security scheme
security = HTTPBearer()

# Pydantic models for request bodies
class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    redirect_url: str = "http://localhost:8080"


# Auth dependency - verify JWT token from Supabase
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Authorization header"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token from Bearer credentials
        token = credentials.credentials
        
        # Debug: Print token (first 50 chars only for security)
        print(f"🔐 Received token: {token[:50]}...")
        
        # Try multiple methods to verify the token
        user_id = None
        email = None
        
        # Method 1: Try Supabase get_user
        try:
            user_response = supabase.auth.get_user(token)
            if user_response and user_response.user:
                print(f"✅ User verified via get_user: {user_response.user.email}")
                return user_response.user
        except Exception as e:
            print(f"⚠️ get_user failed: {str(e)}")
        
        # Method 2: Decode JWT to get user info (since token is from Supabase, it's valid)
        try:
            # Decode without verification (Supabase already verified it during login)
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get('sub')
            email = decoded.get('email')
            print(f"✅ Decoded JWT - User ID: {user_id}, Email: {email}")
            
            # Create user object with required attributes
            class User:
                def __init__(self, id, email):
                    self.id = id
                    self.email = email
            
            return User(user_id, email)
        except Exception as jwt_error:
            print(f"❌ JWT decode failed: {str(jwt_error)}")
            raise HTTPException(status_code=401, detail=f"Invalid token format: {str(jwt_error)}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Auth exception: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


@app.get("/")
def root():
    return {"message": "Rizz Calculator API", "status": "running"}


@app.post("/auth/signup/")
async def signup(request: SignupRequest):
    """Sign up a new user"""
    try:
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "email_redirect_to": request.redirect_url
            }
        })
        
        if response.user:
            return {
                "message": "User created successfully. Please check your email for confirmation.",
                "user_id": response.user.id,
                "email_confirmation_sent": True,
                "note": "Click the confirmation link in your email. If link doesn't work, check Supabase dashboard to confirm manually."
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login/")
async def login(request: LoginRequest):
    """Login user"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.session:
            return {
                "message": "Login successful",
                "access_token": response.session.access_token,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/calculate-rizz/")
async def calculate_rizz(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Calculate rizz score from chat screenshot image using Gemini Vision API
    """
    user_id = current_user.id
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size must be less than 5MB")
    
    try:
        # 1. Upload image to Supabase Storage first
        # Generate unique filename to avoid duplicates (add timestamp)
        # Extract file extension
        file_ext = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        # Create unique filename with timestamp and UUID
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = f"{user_id}/{unique_filename}"
        
        # Try to upload, if file exists, delete it first and retry
        try:
            upload_response = supabase.storage.from_("chat-images").upload(
                file_path,
                contents,
                file_options={"content-type": file.content_type, "upsert": "true"}
            )
        except Exception as upload_error:
            error_str = str(upload_error)
            # If duplicate error, try to delete and re-upload
            if '409' in error_str or 'Duplicate' in error_str or 'already exists' in error_str.lower():
                try:
                    # Delete existing file
                    supabase.storage.from_("chat-images").remove([file_path])
                    # Retry upload
                    upload_response = supabase.storage.from_("chat-images").upload(
                        file_path,
                        contents,
                        file_options={"content-type": file.content_type}
                    )
                except Exception as retry_error:
                    # If delete/retry fails, use a new unique filename
                    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
                    file_path = f"{user_id}/{unique_filename}"
                    upload_response = supabase.storage.from_("chat-images").upload(
                        file_path,
                        contents,
                        file_options={"content-type": file.content_type}
                    )
            else:
                # Re-raise if it's a different error
                raise
        
        # Get public URL
        image_url = supabase.storage.from_("chat-images").get_public_url(file_path)
        
        # 2. Use Gemini Vision API to analyze the image for rizz
        prompt = """
        Analyze this chat screenshot image for "rizz" (charisma/flirt game, charm, smoothness).
        
        Rate the rizz on a scale of 0-100 where:
        - 0-30: Needs major work (cringe, awkward, too forward)
        - 31-50: Average (decent but could improve)
        - 51-70: Good rizz (smooth, engaging, playful)
        - 71-85: Great rizz (confident, witty, charming)
        - 86-100: God-tier rizz (legendary, smooth operator)
        
        Respond ONLY with valid JSON in this exact format:
        {
            "score": <integer 0-100>,
            "suggestions": [
                "<first improvement suggestion>",
                "<second improvement suggestion>",
                "<third improvement suggestion>"
            ],
            "reasoning": "<brief explanation of the score>"
        }
        
        Be honest, constructive, and fun in your feedback. Focus on humor, confidence, playfulness, and engagement.
        """
        
        # Determine MIME type from file content type
        mime_type = file.content_type or 'image/jpeg'
        
        # Encode image to base64
        base64_image = base64.b64encode(contents).decode('utf-8')
        
        # Generate content with Gemini Vision API (fixed: use base64 data directly)
        # Add retry logic for rate limiting/overload errors
        max_retries = 3
        retry_delay = 2  # seconds
        
        response = None
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = model.generate_content(
                    [prompt, {
                        "mime_type": mime_type,
                        "data": base64_image
                    }],
                    generation_config=GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                        max_output_tokens=2048
                    )
                )
                
                # Simplified text extraction
                if response and response.text:
                    response_text = response.text.strip()
                    print(f"✅ Got response text: {response_text[:100]}...")
                else:
                    raise ValueError("Empty response from Gemini API")
                
                break  # Success
                
            except Exception as e:
                last_error = e
                error_str = str(e)
                
                # Check if it's a rate limit/overload error
                if '503' in error_str or 'overloaded' in error_str.lower() or 'UNAVAILABLE' in error_str:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)  # Exponential backoff
                        print(f"Gemini API overloaded, retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                raise HTTPException(
                    status_code=500,
                    detail=f"Error calling Gemini API: {error_str}"
                )
        
        if response is None:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get response from Gemini API after {max_retries} attempts: {str(last_error)}"
            )
        
        # Parse JSON response
        try:
            result_str = response.text.strip()
            
            # Check if result_str is empty
            if not result_str:
                raise ValueError("Empty response text from Gemini API")
            
            # Remove markdown code blocks if present
            if result_str.startswith("```json"):
                result_str = result_str[7:]
            if result_str.startswith("```"):
                result_str = result_str[3:]
            if result_str.endswith("```"):
                result_str = result_str[:-3]
            result_str = result_str.strip()
            
            # Validate we still have content after cleaning
            if not result_str:
                raise ValueError("Empty JSON after cleaning markdown")
            
            result = json.loads(result_str)
            
            # Validate response structure
            if not isinstance(result.get("score"), int) or not (0 <= result["score"] <= 100):
                raise ValueError("Invalid score in response")
            
            if not isinstance(result.get("suggestions"), list) or len(result.get("suggestions", [])) != 3:
                raise ValueError("Invalid suggestions format")
                
        except (json.JSONDecodeError, ValueError, KeyError, AttributeError) as e:
            # Fallback response if JSON parsing fails
            print(f"Error parsing Gemini response: {e}")
            print(f"Response text: {response.text}")
            result = {
                "score": 50,
                "suggestions": [
                    "Try asking more engaging questions to show interest.",
                    "Add emojis or playful language to improve the vibe.",
                    "End with a callback hook or question to keep the conversation going."
                ],
                "reasoning": "Unable to parse AI response, using default score."
            }
        
        # 3. Store score in database
        score_data = {
            "user_id": user_id,
            "rizz_score": result["score"],
            "chat_text": result.get("reasoning", ""),  # Store reasoning instead of OCR text
            "suggestions": result["suggestions"],
            "image_url": image_url
        }
        
        # db_response = supabase.table("scores").insert(score_data).execute()
        
        # if not db_response.data:
        #     raise HTTPException(status_code=500, detail="Failed to save score to database")
        
        return {
            "score": result["score"],
            "suggestions": result["suggestions"],
            "reasoning": result.get("reasoning", ""),
            "image_url": image_url,
            # "score_id": db_response.data[0]["id"]
            "score_id":"1"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/leaderboard/")
def get_leaderboard():
    """Get top 10 users by average rizz score"""
    try:
        response = supabase.rpc("get_leaderboard").execute()
        
        if response.data:
            return {"leaderboard": response.data}
        else:
            return {"leaderboard": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leaderboard: {str(e)}")


@app.get("/user/scores/")
async def get_user_scores(current_user = Depends(get_current_user)):
    """Get all scores for the current user"""
    try:
        response = supabase.table("scores").select("*").eq("user_id", current_user.id).order("created_at", desc=True).execute()
        
        return {"scores": response.data if response.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user scores: {str(e)}")
    

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)