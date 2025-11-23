# Meme Templates Directory

This directory contains the base meme template images used for generating personalized rizz memes.

## How to Add Meme Templates

1. **Add the image file** to this directory:
   - Name it according to the template ID in `meme_templates.py`
   - Example: `disaster_girl.jpg`, `spiderman_pointing.jpg`, etc.
   - Supported formats: JPG, PNG

2. **Update `meme_templates.py`**:
   - The template configuration already exists
   - Just make sure the `image_path` matches your filename
   - Example: `"image_path": "templates/disaster_girl.jpg"`

## Template Images Needed

Based on `meme_templates.py`, you need these images:

- `disaster_girl.jpg` - Disaster Girl meme template
- `spiderman_pointing.jpg` - Spider-Man pointing meme template  
- `success_kid.jpg` - Success Kid meme template
- `doge.jpg` - Doge meme template

## Where to Get Templates

You can find these meme templates from:
- [Know Your Meme](https://knowyourmeme.com)
- [Imgflip Meme Generator](https://imgflip.com/memegenerator) - Download blank templates
- Google Images search: "[meme name] template"

## Image Requirements

- **Format**: JPG or PNG
- **Recommended size**: 600x500 pixels (or matching template size)
- **Quality**: High resolution for best text overlay results
- **Background**: Should be clear/blank where text will be overlaid

## Notes

- If a template image is missing, the system will create a placeholder
- Text positioning is defined in `meme_templates.py`
- You can customize text positions, colors, and fonts in the template config

