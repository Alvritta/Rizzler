# 🎨 Meme Generation Setup Guide

## Overview

The Rizz Calculator now generates personalized memes with your rizz score! Each report includes a randomly selected meme template with your score overlaid.

## How It Works

1. **Template Selection**: Randomly picks from available meme templates
2. **Text Overlay**: Uses Pillow (PIL) to overlay text on the template
3. **Upload**: Uploads the generated meme to Supabase Storage
4. **Display**: Shows the meme in the Results page

## Setup Steps

### 1. Install Dependencies

Pillow is already in `requirements.txt`, so if you've installed dependencies, you're good!

```bash
pip install pillow
```

### 2. Add Meme Template Images

Create a `templates/` folder in the backend directory:

```bash
mkdir RC/backend/templates
```

Then add meme template images:
- `disaster_girl.jpg`
- `spiderman_pointing.jpg`
- `success_kid.jpg`
- `doge.jpg`

**Where to get templates:**
- Download blank templates from [Imgflip](https://imgflip.com/memegenerator)
- Or search "[meme name] template" on Google Images
- Make sure they're high quality (600x500px recommended)

### 3. Test It

Run your backend and test the `/calculate_rizz/` endpoint. The response will now include:
```json
{
  "score": 68,
  "suggestions": [...],
  "reasoning": "...",
  "image_url": "...",
  "meme_url": "https://..."  // NEW!
}
```

## Customizing Memes

### Add New Templates

1. Add image to `templates/` folder
2. Add config to `meme_templates.py`:

```python
{
    "id": "your_meme_id",
    "name": "Your Meme Name",
    "image_path": "templates/your_meme.jpg",
    "texts": [
        {
            "position": (x, y),  # Text position
            "text_template": "Your text with {score}",
            "font_size": 40,
            "color": (255, 255, 255),  # RGB
            "stroke_color": (0, 0, 0),  # Outline color
            "stroke_width": 2,
            "max_width": 500,
            "align": "left"  # or "center" or "right"
        }
    ],
    "image_size": (600, 500)
}
```

### Customize Text Positions

Edit the `position` tuple `(x, y)` in `meme_templates.py`:
- `x`: Distance from left edge
- `y`: Distance from top edge

### Customize Fonts

The system tries to use Impact font (classic meme font), but falls back to system fonts. To use a custom font:

1. Add font file to `backend/fonts/` folder
2. Update `get_font()` in `meme_generator.py` to use your font

## Troubleshooting

### "Template image not found"
- Make sure images are in `RC/backend/templates/` folder
- Check filenames match `image_path` in `meme_templates.py`
- System will create a placeholder if image is missing

### "Meme generation failed"
- Check Pillow is installed: `pip install pillow`
- Check Supabase storage permissions
- Check backend logs for detailed error

### Text not displaying correctly
- Adjust `position` coordinates in template config
- Increase `font_size` if text is too small
- Adjust `max_width` for text wrapping

### Font issues
- System will fallback to default font if custom font not found
- Check font file path in `get_font()` function

## File Structure

```
RC/backend/
├── templates/          # Meme template images
│   ├── disaster_girl.jpg
│   ├── spiderman_pointing.jpg
│   ├── success_kid.jpg
│   └── doge.jpg
├── meme_templates.py    # Template configurations
├── meme_generator.py   # Meme generation logic
└── main.py            # Uses meme_generator
```

## Production Deployment

When deploying:
1. **Include templates folder** in your deployment
2. **Or upload templates to Supabase Storage** and update paths
3. **Or use absolute URLs** for templates hosted elsewhere

The generated memes are uploaded to Supabase Storage, so they'll work in production!

## Future Enhancements

- [ ] More meme templates
- [ ] Score-based template selection (different memes for different score ranges)
- [ ] Custom font support
- [ ] Animated memes (GIF support)
- [ ] User-uploaded meme templates

