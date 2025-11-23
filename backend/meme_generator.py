"""
Meme generator using Pillow to overlay text on meme templates
"""
from PIL import Image, ImageDraw, ImageFont
import os
import io
from typing import Dict, Optional
from meme_templates import get_random_template, get_template_by_id


def get_font(font_size: int, bold: bool = False) -> Optional[ImageFont.FreeTypeFont]:
    """Get a font, trying different options"""
    try:
        # Try to use a system font (Impact is classic for memes)
        if os.name == 'nt':  # Windows
            font_path = "C:/Windows/Fonts/impact.ttf"
        elif os.name == 'posix':  # macOS/Linux
            font_path = "/System/Library/Fonts/Supplemental/Impact.ttf"  # macOS
            if not os.path.exists(font_path):
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Linux fallback
        else:
            font_path = None
        
        if font_path and os.path.exists(font_path):
            return ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"⚠️ Could not load custom font: {e}")
    
    # Fallback to default font
    try:
        return ImageFont.truetype("arial.ttf", font_size)
    except:
        return ImageFont.load_default()


def generate_meme(score: int, template_id: Optional[str] = None) -> bytes:
    """
    Generate a meme image with the rizz score
    
    Args:
        score: The rizz score (0-100)
        template_id: Optional template ID, if None picks random
    
    Returns:
        bytes: Image bytes (PNG format)
    """
    # Get template - random selection if no template_id provided
    if template_id:
        template = get_template_by_id(template_id)
    else:
        # Randomly pick from available templates
        template = get_random_template()
    
    # Verify template image exists, if not try to find an available one
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(backend_dir, template["image_path"])
    
    if not os.path.exists(template_path) and not os.path.exists(template["image_path"]):
        # Template image doesn't exist, try to find another available template
        print(f"⚠️ Template {template['id']} image not found, looking for alternatives...")
        from meme_templates import MEME_TEMPLATES
        for alt_template in MEME_TEMPLATES:
            alt_path = os.path.join(backend_dir, alt_template["image_path"])
            if os.path.exists(alt_path) or os.path.exists(alt_template["image_path"]):
                print(f"✅ Using alternative template: {alt_template['name']}")
                template = alt_template
                break
    
    print(f"🎨 Generating meme with template: {template['name']} (ID: {template['id']})")
    
    # Load base image - resolve path relative to backend directory
    base_image_path = template["image_path"]
    
    # Try to resolve path relative to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    full_image_path = os.path.join(backend_dir, base_image_path)
    
    # Check if image exists
    if not os.path.exists(full_image_path):
        print(f"⚠️ Template image not found: {full_image_path}, trying: {base_image_path}")
        if os.path.exists(base_image_path):
            full_image_path = base_image_path
            img = Image.open(full_image_path)
            # Resize if needed
            if img.size != tuple(template["image_size"]):
                img = img.resize(template["image_size"], Image.Resampling.LANCZOS)
        else:
            print(f"⚠️ Creating placeholder for missing template: {template['name']}")
            # Create a placeholder image
            img = Image.new('RGB', template["image_size"], color=(200, 200, 200))
            draw = ImageDraw.Draw(img)
            # Draw a simple placeholder
            draw.rectangle([10, 10, template["image_size"][0]-10, template["image_size"][1]-10], 
                          outline=(100, 100, 100), width=3)
            draw.text((template["image_size"][0]//2, template["image_size"][1]//2), 
                     f"Meme Template: {template['name']}\n(Add image: {base_image_path})", 
                     fill=(0, 0, 0), anchor="mm")
    else:
        # Image exists, load it
        img = Image.open(full_image_path)
        # Resize if needed
        if img.size != tuple(template["image_size"]):
            img = img.resize(template["image_size"], Image.Resampling.LANCZOS)
    
    draw = ImageDraw.Draw(img)
    
    # Overlay text
    for text_config in template["texts"]:
        # Format text with score
        text = text_config["text_template"].format(score=score)
        
        # Get font
        font = get_font(text_config["font_size"], bold=True)
        
        # Get text position
        position = text_config["position"]
        
        # Handle text wrapping if max_width is specified
        if text_config.get("max_width"):
            # Simple word wrapping
            words = text.split()
            lines = []
            current_line = []
            current_width = 0
            
            for word in words:
                # Approximate text width (rough estimate)
                word_width = len(word) * (text_config["font_size"] * 0.6)
                if current_width + word_width > text_config["max_width"] and current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:
                    current_line.append(word)
                    current_width += word_width + (text_config["font_size"] * 0.3)
            
            if current_line:
                lines.append(" ".join(current_line))
            
            text = "\n".join(lines)
        
        # Split text into lines for multiline handling
        text_lines = text.split("\n")
        is_multiline = len(text_lines) > 1
        
        # Get line height for multiline spacing
        if is_multiline:
            # Approximate line height
            line_height = text_config["font_size"] + 10
        
        # Draw text with stroke (outline)
        if text_config.get("stroke_width", 0) > 0:
            for line_idx, line_text in enumerate(text_lines):
                if not line_text.strip():
                    continue
                    
                # Calculate y position for this line
                y_pos = position[1] + (line_idx * line_height if is_multiline else 0)
                
                # Draw stroke for this line
                for adj in range(-text_config["stroke_width"], text_config["stroke_width"] + 1):
                    for adj2 in range(-text_config["stroke_width"], text_config["stroke_width"] + 1):
                        if adj != 0 or adj2 != 0:
                            if is_multiline:
                                # For multiline, don't use anchor
                                draw.text(
                                    (position[0] + adj, y_pos + adj2),
                                    line_text,
                                    font=font,
                                    fill=text_config["stroke_color"]
                                )
                            else:
                                # For single line, use anchor
                                draw.text(
                                    (position[0] + adj, y_pos + adj2),
                                    line_text,
                                    font=font,
                                    fill=text_config["stroke_color"],
                                    anchor="lt" if text_config.get("align") == "left" else 
                                           "mt" if text_config.get("align") == "center" else "rt"
                                )
        
        # Draw main text
        for line_idx, line_text in enumerate(text_lines):
            if not line_text.strip():
                continue
                
            # Calculate y position for this line
            y_pos = position[1] + (line_idx * line_height if is_multiline else 0)
            
            if is_multiline:
                # For multiline, don't use anchor
                draw.text(
                    (position[0], y_pos),
                    line_text,
                    font=font,
                    fill=text_config["color"]
                )
            else:
                # For single line, use anchor
                draw.text(
                    (position[0], y_pos),
                    line_text,
                    font=font,
                    fill=text_config["color"],
                    anchor="lt" if text_config.get("align") == "left" else 
                           "mt" if text_config.get("align") == "center" else "rt"
                )
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()


def generate_meme_and_upload(score: int, supabase_client, template_id: Optional[str] = None) -> str:
    """
    Generate meme and upload to Supabase Storage
    
    Args:
        score: The rizz score
        supabase_client: Supabase client instance
        template_id: Optional template ID
    
    Returns:
        str: Public URL of the uploaded meme
    """
    # Generate meme image
    meme_bytes = generate_meme(score, template_id)
    
    # Upload to Supabase
    from datetime import datetime
    import uuid
    
    unique_filename = f"memes/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.png"
    
    upload_response = supabase_client.storage.from_("chat-images").upload(
        unique_filename,
        meme_bytes,
        file_options={"content-type": "image/png", "upsert": "true"}
    )
    
    # Get public URL
    meme_url = supabase_client.storage.from_("chat-images").get_public_url(unique_filename)
    
    print(f"✅ Meme uploaded: {meme_url}")
    
    return meme_url

