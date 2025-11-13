from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client, Client
import io
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from typing import Optional

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

# Initialize Gemini Client
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
            import jwt
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
        import uuid
        from datetime import datetime
        
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
        
        # Generate content with Gemini Vision API using the new client format
        # Add retry logic for rate limiting/overload errors
        import time
        max_retries = 3
        retry_delay = 2  # seconds
        
        response = None
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[
                        types.Part.from_bytes(
                            data=contents,
                            mime_type=mime_type,
                        ),
                        prompt
                    ],
                    config={
                        'response_mime_type': 'application/json',
                        'temperature': 0.7,
                        'max_output_tokens': 500
                    }
                )
                
                # Check if response is valid and has content
                if response is None:
                    raise ValueError("Empty response from Gemini API")
                
                # Try to get text from response - google-genai GenerateContentResponse structure
                response_text = None
                
                # Method 1: Access via candidates[0].content.parts[0].text (standard structure)
                try:
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content'):
                            content = candidate.content
                            # Check if content has parts attribute
                            if hasattr(content, 'parts'):
                                parts = content.parts
                                if parts and len(parts) > 0:
                                    part = parts[0]
                                    # Check if part has text attribute
                                    if hasattr(part, 'text') and part.text:
                                        response_text = part.text
                                        print(f"✅ Got text via candidates[0].content.parts[0].text: {response_text[:100]}...")
                                    # Also try accessing part as string if it's a TextPart
                                    elif hasattr(part, '__str__'):
                                        part_str = str(part)
                                        if part_str and len(part_str) > 10:
                                            response_text = part_str
                                            print(f"✅ Got text via part string: {response_text[:100]}...")
                except Exception as e:
                    print(f"Method 1 (candidates) failed: {e}")
                
                # Method 2: Try parsed attribute if available
                if not response_text:
                    try:
                        if hasattr(response, 'parsed') and response.parsed:
                            response_text = str(response.parsed)
                            print(f"✅ Got text via parsed: {response_text[:100]}...")
                    except Exception as e:
                        print(f"Method 2 (parsed) failed: {e}")
                
                # Method 3: Try sdk_http_response if available
                if not response_text:
                    try:
                        if hasattr(response, 'sdk_http_response'):
                            http_response = response.sdk_http_response
                            if hasattr(http_response, 'body'):
                                body = http_response.body
                                if body:
                                    response_text = body.decode('utf-8') if isinstance(body, bytes) else str(body)
                                    print(f"✅ Got text via sdk_http_response.body: {response_text[:100]}...")
                    except Exception as e:
                        print(f"Method 3 (sdk_http_response) failed: {e}")
                
                # Method 4: Try direct .text attribute
                if not response_text:
                    try:
                        if hasattr(response, 'text') and response.text:
                            response_text = str(response.text)
                            print(f"✅ Got text via .text: {response_text[:100]}...")
                    except Exception as e:
                        print(f"Method 4 (.text) failed: {e}")
                
                # Method 5: Debug - print structure and try to access parts directly
                if not response_text:
                    print(f"\n=== DEBUG: Trying to access parts directly ===")
                    try:
                        candidate = response.candidates[0]
                        content = candidate.content
                        print(f"Content type: {type(content)}")
                        print(f"Content attributes: {[a for a in dir(content) if not a.startswith('_')]}")
                        
                        # Try to get parts
                        if hasattr(content, 'parts'):
                            parts = content.parts
                            print(f"Parts: {parts}")
                            print(f"Parts type: {type(parts)}")
                            print(f"Parts length: {len(parts) if parts else 0}")
                            
                            if parts and len(parts) > 0:
                                part = parts[0]
                                print(f"Part type: {type(part)}")
                                print(f"Part: {part}")
                                print(f"Part attributes: {[a for a in dir(part) if not a.startswith('_')]}")
                                
                                # Try all possible ways to get text from part
                                for attr in ['text', 'content', 'data', 'value']:
                                    if hasattr(part, attr):
                                        attr_val = getattr(part, attr)
                                        if attr_val:
                                            response_text = str(attr_val)
                                            print(f"✅ Found text via part.{attr}: {response_text[:100]}...")
                                            break
                    except Exception as e:
                        print(f"Debug access failed: {e}")
                    print(f"=== END DEBUG ===\n")
                
                if not response_text:
                    raise ValueError(f"Could not extract text from Gemini response. Type: {type(response)}, Response: {response}")
                
                # Ensure response has text attribute for parsing code below
                if not hasattr(response, 'text') or response.text is None:
                    response.text = response_text
                
                break  # Success, exit retry loop
                
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
                    else:
                        raise HTTPException(
                            status_code=503,
                            detail=f"Gemini API is currently overloaded. Please try again in a few moments. Error: {error_str}"
                        )
                else:
                    # Not a retryable error, raise immediately
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
            # Check if response has text attribute and it's not None
            if not hasattr(response, 'text') or response.text is None:
                raise ValueError("Empty response from Gemini API")
            
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
            print(f"Response type: {type(response)}")
            print(f"Response text: {response.text if hasattr(response, 'text') else 'No text attribute'}")
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
        
        db_response = supabase.table("scores").insert(score_data).execute()
        
        if not db_response.data:
            raise HTTPException(status_code=500, detail="Failed to save score to database")
        
        return {
            "score": result["score"],
            "suggestions": result["suggestions"],
            "reasoning": result.get("reasoning", ""),
            "image_url": image_url,
            "score_id": db_response.data[0]["id"]
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

