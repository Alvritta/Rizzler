from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from supabase import create_client, Client
import io
import os
import json
import base64
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import time
import uuid
from datetime import datetime

load_dotenv()

# Import meme generator (after load_dotenv to ensure paths are set)
try:
    from meme_generator import generate_meme_and_upload
except ImportError:
    print("⚠️ Warning: meme_generator not found, meme generation disabled")
    generate_meme_and_upload = None

app = FastAPI(title="Rizz Calculator API", version="1.0.0")

# CORS middleware
# Get frontend URL from environment variable, fallback to * for development
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
allowed_origins = [FRONTEND_URL] if FRONTEND_URL != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for request validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    body_str = body.decode('utf-8', errors='ignore') if body else ""
    
    print(f"\n{'='*60}")
    print(f"❌ VALIDATION ERROR in {request.method} {request.url}")
    print(f"{'='*60}")
    print(f"📥 Request body: {body_str}")
    print(f"📥 Request headers: {dict(request.headers)}")
    print(f"📥 Validation errors: {exc.errors()}")
    print(f"{'='*60}\n")
    
    return JSONResponse(
        status_code=400,
        content={"detail": f"Validation error: {exc.errors()}", "body": body_str}
    )

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# Pydantic models for request bodies
class CalculateRizzRequest(BaseModel):
    image_url: str
    nickname: str


@app.get("/")
def root():
    return {"message": "Rizz Calculator API", "status": "running"}


@app.post("/upload_screenshot/")
async def upload_screenshot(file: UploadFile = File(...)):
    """
    Upload a chat screenshot image (Button 1)
    Returns the image URL for use in calculate_rizz endpoint
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size must be less than 5MB")
    
    try:
        # Generate unique filename to avoid duplicates
        file_ext = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = f"guest/{unique_filename}"
        
        # Upload to Supabase Storage
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
                    supabase.storage.from_("chat-images").remove([file_path])
                    upload_response = supabase.storage.from_("chat-images").upload(
                        file_path,
                        contents,
                        file_options={"content-type": file.content_type}
                    )
                except Exception as retry_error:
                    # If delete/retry fails, use a new unique filename
                    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
                    file_path = f"guest/{unique_filename}"
                    upload_response = supabase.storage.from_("chat-images").upload(
                        file_path,
                        contents,
                        file_options={"content-type": file.content_type}
                    )
            else:
                raise
        
        # Get public URL
        image_url = supabase.storage.from_("chat-images").get_public_url(file_path)
        print(f"✅ Upload successful, file_path: {file_path}, image_url: {image_url}")
        
        return {
            "success": True,
            "image_url": image_url,
            "message": "Screenshot uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")


@app.post("/calculate_rizz/")
async def calculate_rizz(request: CalculateRizzRequest):
    """
    Calculate rizz score from uploaded screenshot image URL (Button 2)
    Requires image_url from upload_screenshot endpoint and nickname
    """
    print(f"\n{'='*60}")
    print(f"🔍 CALCULATE_RIZZ ENDPOINT CALLED")
    print(f"{'='*60}")
    print(f"📥 Request received: {request}")
    print(f"📥 Request type: {type(request)}")
    
    try:
        request_dict = request.model_dump() if hasattr(request, 'model_dump') else request.dict() if hasattr(request, 'dict') else str(request)
        print(f"📥 Request dict: {request_dict}")
    except Exception as e:
        print(f"⚠️ Could not dump request: {e}")
        request_dict = str(request)
    
    image_url = request.image_url
    nickname = request.nickname.strip() if request.nickname else ""
    
    print(f"📝 Image URL: {image_url}")
    print(f"📝 Nickname: {nickname}")
    
    if not image_url:
        print(f"❌ ERROR: image_url is missing or empty")
        raise HTTPException(status_code=400, detail="image_url is required")
    
    if not nickname:
        print(f"❌ ERROR: nickname is missing or empty")
        raise HTTPException(status_code=400, detail="nickname is required")
    
    if len(nickname) > 30:
        print(f"❌ ERROR: nickname too long")
        raise HTTPException(status_code=400, detail="nickname must be 30 characters or less")
    
    if not isinstance(image_url, str):
        print(f"❌ ERROR: image_url is not a string. Type: {type(image_url)}")
        raise HTTPException(status_code=400, detail=f"image_url must be a string, got {type(image_url)}")
    
    print(f"✅ Image URL validated: {image_url[:50]}...")
    print(f"✅ Nickname validated: {nickname}")
    
    try:
        print(f"\n📥 Step 1: Downloading image from Supabase Storage...")
        print(f"   Image URL: {image_url}")
        
        # Extract file path from URL
        # URL format: https://<project>.supabase.co/storage/v1/object/public/<bucket>/<path>
        # Or: https://<project>.supabase.co/storage/v1/object/sign/<bucket>/<path>?token=...
        try:
            # Try to extract path from public URL
            if '/object/public/' in image_url:
                # Public URL format
                path_start = image_url.find('/object/public/') + len('/object/public/')
                bucket_and_path = image_url[path_start:]
                bucket_end = bucket_and_path.find('/')
                bucket_name = bucket_and_path[:bucket_end]
                file_path = bucket_and_path[bucket_end + 1:]
                print(f"   Extracted bucket: {bucket_name}")
                print(f"   Extracted path: {file_path}")
                
                # Download directly from Supabase Storage
                file_data = supabase.storage.from_(bucket_name).download(file_path)
                contents = file_data
                
                # Detect MIME type from file extension
                file_ext = os.path.splitext(file_path)[1].lower()
                mime_types = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }
                mime_type = mime_types.get(file_ext, 'image/jpeg')
                
            elif '/object/sign/' in image_url:
                # Signed URL - use HTTP GET
                print(f"   Using signed URL, downloading via HTTP...")
                image_response = requests.get(image_url, timeout=30)
                if image_response.status_code != 200:
                    print(f"❌ ERROR: Failed to download signed URL. Status: {image_response.status_code}")
                    raise HTTPException(status_code=400, detail=f"Failed to download image: Status {image_response.status_code}")
                contents = image_response.content
                mime_type = image_response.headers.get('content-type', 'image/jpeg')
            else:
                # Fallback: try HTTP GET
                print(f"   Unknown URL format, trying HTTP GET...")
                image_response = requests.get(image_url, timeout=30)
                if image_response.status_code != 200:
                    print(f"❌ ERROR: Failed to download image. Status: {image_response.status_code}")
                    print(f"   Response text: {image_response.text[:200]}")
                    raise HTTPException(status_code=400, detail=f"Failed to download image from URL: {image_url}. Status: {image_response.status_code}")
                contents = image_response.content
                mime_type = image_response.headers.get('content-type', 'image/jpeg')
            
            print(f"✅ Image downloaded successfully")
            print(f"   Size: {len(contents)} bytes ({len(contents) / 1024:.2f} KB)")
            print(f"   MIME type: {mime_type}")
            
        except Exception as e:
            print(f"❌ ERROR: Exception downloading image: {str(e)}")
            print(f"   Error type: {type(e)}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")
        
        # Validate file size (max 5MB)
        if len(contents) > 5 * 1024 * 1024:
            print(f"❌ ERROR: Image too large: {len(contents)} bytes")
            raise HTTPException(status_code=400, detail="Image size must be less than 5MB")
        
        print(f"✅ File size validated")
        
        # Use Gemini Vision API to analyze the image for rizz
        # prompt = """
        # Analyze this chat screenshot image for "rizz" (charisma/flirt game, charm, smoothness).
        
        # Rate the rizz on a scale of 0-100 where:
        # - 0-30: Needs major work (cringe, awkward, too forward)
        # - 31-50: Average (decent but could improve)
        # - 51-70: Good rizz (smooth, engaging, playful)
        # - 71-85: Great rizz (confident, witty, charming)
        # - 86-100: God-tier rizz (legendary, smooth operator)
        
        # Respond ONLY with valid JSON in this exact format:
        # {
        #     "score": <integer 0-100>,
        #     "suggestions": [
        #         "<first improvement suggestion>",
        #         "<second improvement suggestion>",
        #         "<third improvement suggestion>"
        #     ],
        #     "reasoning": "<brief explanation of the score>"
        # }
        
        # Be honest, constructive, and fun in your feedback. Focus on humor, confidence, playfulness, and engagement.
        # """
        prompt = """
        ### ROLE & OBJECTIVE
You are a brutally honest, elite dating coach and social dynamics expert. Your job is to evaluate the "Rizz" (flirting skill, wit, and charm) of a user's chat conversation. 

*CRITICAL INSTRUCTION:* Do NOT be polite. Do NOT give "participation trophies." Most people are boring—your scoring must reflect that. 

### SCORING RUBRIC (USE THE FULL SCALE)
You must use the full range of 0-100. Do not bunch scores around 70.
- *0-30 (The "L" Zone):* Cringey, desperate, boring one-word replies, double-texting without response, or interviewing (asking too many questions).
- *31-50 (NPC Energy):* Polite but boring. Safe, logical, friendly, but zero sexual tension or excitement. This is the default score for "normal" texts.
- *51-75 (Solid Game):* Playful, teasing, uses "push-pull," emotional spikes, or good banter. 
- *76-90 (Rizzler):* genuinely witty, confident, takes risks that pay off, dominant frame.
- *91-100 (God Tier):* Viral-worthy smoothness. Extremely rare.

### ANALYSIS STEPS
1. *Detect Dryness:* Is the user just answering questions? (Minus points).
2. *Detect Desperation:* Are they replying instantly with paragraphs to short texts? (Major minus points).
3. *Detect Wit:* Did they tease, roleplay, or misinterpret on purpose? (Plus points).

### OUTPUT FORMAT
Respond ONLY with valid JSON. No markdown, no backticks.
{
    "score": <integer 0-100>,
    "suggestions": [
        "<first specific actionable tip>",
        "<second specific actionable tip>",
        "<third specific actionable tip>"
    ],
    "reasoning": "<2-3 sentences. Be punchy and direct. Roast them if the score is low. Praise them if high. Explain EXACTLY why they got this score.>"
}

CRITICAL: suggestions MUST be an array of exactly 3 strings. Each suggestion should be a specific, actionable tip.

        """
        # prompt="""
#         prompt = """
#         You are an expert social dynamics coach and "Rizz" consultant specializing in Gen Z dating culture and digital communication. Your task is to analyze the provided chat screenshot or text for "rizz" (charisma, wit, confidence, and game).

# ANALYSIS RUBRIC
# Evaluate the interaction based on these weighted dimensions:

# Confidence (Leadership, lack of desperation)

# Wit & Humor (Playfulness, banter, clever callbacks)

# Personalization (Referencing their profile/interests vs. generic lines)

# Flow (Vibe check, response timing, moving the conversation forward)

# SCORING SCALE
# 0-30: L Rizz (Awkward, cringey, too intense, or boring/dry).

# 31-50: Mid Rizz (Average, polite but forgettable, "NPC energy").

# 51-70: W Rizz (Solid, smooth, engaging, likely to get a reply).

# 71-85: High Rizz (Charming, confident, stands out).

# 86-100: God-Tier Rizz (Legendary, effortless, viral-worthy).

# OUTPUT FORMAT
# You must respond with valid JSON only. Do not include markdown formatting (likejson). The structure must be: { "score": <integer_0_to_100>, "rizz_level": "<string_from_scale_above>", "best_line": "<string_quote_from_user_or_null>", "constructive_feedback": [ "<specific_actionable_tip_1>", "<specific_actionable_tip_2>" ], "reasoning": "<short_punchy_explanation_of_the_score_max_2_sentences>" }

#         """
        
        print(f"\n📥 Step 2: Encoding image to base64...")
        # Encode image to base64
        base64_image = base64.b64encode(contents).decode('utf-8')
        print(f"✅ Base64 encoded: {len(base64_image)} characters")
        
        print(f"\n📥 Step 3: Calling Gemini Vision API...")
        # Generate content with Gemini Vision API
        # Add retry logic for rate limiting/overload errors
        max_retries = 3
        retry_delay = 2  # seconds
        
        response = None
        last_error = None
        
        for attempt in range(max_retries):
            try:
                print(f"   Attempt {attempt + 1}/{max_retries}")
                print(f"   MIME type: {mime_type}")
                print(f"   Base64 length: {len(base64_image)}")
                
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
                
                print(f"   Gemini response received")
                print(f"   Response type: {type(response)}")
                
                # Simplified text extraction
                if response and response.text:
                    response_text = response.text.strip()
                    print(f"✅ Got response text: {response_text[:100]}...")
                else:
                    print(f"❌ ERROR: Empty response from Gemini API")
                    print(f"   Response: {response}")
                    raise ValueError("Empty response from Gemini API")
                
                break  # Success
                
            except Exception as e:
                last_error = e
                error_str = str(e)
                print(f"❌ ERROR in attempt {attempt + 1}: {error_str}")
                print(f"   Error type: {type(e)}")
                
                # Check if it's a rate limit/overload error
                if '503' in error_str or 'overloaded' in error_str.lower() or 'UNAVAILABLE' in error_str:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)  # Exponential backoff
                        print(f"⚠️ Gemini API overloaded, retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                print(f"❌ Fatal error, not retrying")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error calling Gemini API: {error_str}"
                )
        
        if response is None:
            print(f"❌ ERROR: No response after {max_retries} attempts")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get response from Gemini API after {max_retries} attempts: {str(last_error)}"
            )
        
        print(f"\n📥 Step 4: Parsing JSON response...")
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
            
            # Handle suggestions - convert string to array if needed
            suggestions = result.get("suggestions", [])
            if isinstance(suggestions, str):
                # If Gemini returned a single string, split it into 3 suggestions
                print(f"⚠️ WARNING: Suggestions is a string, converting to array")
                # Try to split by periods or newlines, or create 3 suggestions from the string
                suggestions_list = [s.strip() for s in suggestions.split('.') if s.strip()][:3]
                # If we don't have 3, pad with generic suggestions
                while len(suggestions_list) < 3:
                    suggestions_list.append("Keep practicing and refining your approach.")
                result["suggestions"] = suggestions_list[:3]
            elif not isinstance(suggestions, list):
                raise ValueError("Suggestions must be an array")
            elif len(suggestions) != 3:
                # If we have fewer than 3, pad with generic ones
                print(f"⚠️ WARNING: Got {len(suggestions)} suggestions, expected 3")
                while len(suggestions) < 3:
                    suggestions.append("Keep practicing and refining your approach.")
                result["suggestions"] = suggestions[:3]
                
        except (json.JSONDecodeError, ValueError, KeyError, AttributeError) as e:
            # Fallback response if JSON parsing fails
            print(f"❌ ERROR parsing JSON: {e}")
            print(f"   Error type: {type(e)}")
            print(f"   Response text: {response.text if hasattr(response, 'text') else 'No text attribute'}")
            print(f"   Response: {response}")
            result = {
                "score": 50,
                "suggestions": [
                    "Try asking more engaging questions to show interest.",
                    "Add emojis or playful language to improve the vibe.",
                    "End with a callback hook or question to keep the conversation going."
                ],
                "reasoning": "Unable to parse AI response, using default score."
            }
        
        print(f"✅ JSON parsed successfully")
        print(f"   Score: {result['score']}")
        print(f"   Suggestions count: {len(result.get('suggestions', []))}")
        
        print(f"\n📤 Step 5: Generating meme...")
        # Generate meme with the rizz score
        meme_url = None
        if generate_meme_and_upload:
            try:
                meme_url = generate_meme_and_upload(result["score"], supabase)
                print(f"✅ Meme generated: {meme_url}")
            except Exception as e:
                print(f"⚠️ Meme generation failed: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
                meme_url = None  # Continue without meme if generation fails
        else:
            print(f"⚠️ Meme generation disabled (module not found)")
        
        print(f"\n📤 Step 6: Storing score in database...")
        # Store score in Supabase with nickname
        try:
            score_data = {
                "nickname": nickname,
                "rizz_score": result["score"],
                "suggestions": result["suggestions"],
                "reasoning": result.get("reasoning", ""),
                "image_url": image_url,
                "meme_url": meme_url
            }
            
            db_response = supabase.table("scores").insert(score_data).execute()
            print(f"✅ Score stored in database")
            print(f"   Score ID: {db_response.data[0]['id'] if db_response.data else 'N/A'}")
        except Exception as e:
            print(f"⚠️ Failed to store score in database: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            # Continue even if database storage fails
        
        print(f"\n📤 Step 7: Returning response...")
        print(f"{'='*60}\n")
        
        return {
            "score": result["score"],
            "suggestions": result["suggestions"],
            "reasoning": result.get("reasoning", ""),
            "image_url": image_url,
            "meme_url": meme_url,
            "nickname": nickname
        }
        
    except HTTPException as e:
        print(f"\n❌ HTTPException raised: {e.status_code} - {e.detail}")
        print(f"{'='*60}\n")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        print(f"{'='*60}\n")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/leaderboard/")
def get_leaderboard():
    """
    Get top 10 users by average rizz score (grouped by nickname)
    """
    try:
        # Use Supabase function if available, otherwise query directly
        try:
            response = supabase.rpc("get_leaderboard").execute()
            if response.data:
                return {"leaderboard": response.data}
        except Exception as rpc_error:
            print(f"⚠️ RPC function not available, using direct query: {rpc_error}")
        
        # Fallback: Direct query
        response = supabase.table("scores").select("nickname, rizz_score").execute()
        
        if not response.data:
            return {"leaderboard": []}
        
        # Group by nickname and calculate average
        nickname_scores = {}
        for score in response.data:
            nickname = score.get("nickname", "Anonymous")
            if nickname not in nickname_scores:
                nickname_scores[nickname] = []
            nickname_scores[nickname].append(score.get("rizz_score", 0))
        
        # Calculate averages and sort
        leaderboard = []
        for nickname, scores in nickname_scores.items():
            avg_score = sum(scores) / len(scores)
            leaderboard.append({
                "nickname": nickname,
                "avg_rizz": round(avg_score),
                "total_scores": len(scores)
            })
        
        # Sort by average score (descending) and limit to top 10
        leaderboard.sort(key=lambda x: x["avg_rizz"], reverse=True)
        leaderboard = leaderboard[:10]
        
        return {"leaderboard": leaderboard}
        
    except Exception as e:
        print(f"❌ Error fetching leaderboard: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error fetching leaderboard: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
