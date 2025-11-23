"""
Meme template configurations for Rizz Calculator
Each template defines text positions, fonts, colors, and the base image path
"""
import random
from typing import Dict, List, Tuple

# Meme template configurations
MEME_TEMPLATES = [
    {
        "id": "disaster_girl",
        "name": "Disaster Girl",
        "image_path": "templates/disaster_girl.jpg",
        "texts": [
            {
                "position": (50, 30),  # (x, y) from top-left
                "text_template": "My Crush's DMs after I sent a risky text",
                "font_size": 40,
                "color": (255, 255, 255),  # White
                "stroke_color": (0, 0, 0),  # Black outline
                "stroke_width": 2,
                "max_width": 500,
                "align": "left"
            },
            {
                "position": (50, 400),
                "text_template": "Me, having a Rizz Score of {score} and not caring",
                "font_size": 35,
                "color": (255, 255, 255),
                "stroke_color": (0, 0, 0),
                "stroke_width": 2,
                "max_width": 500,
                "align": "left"
            }
        ],
        "image_size": (600, 500)  # (width, height)
    },
    {
        "id": "spiderman_pointing",
        "name": "Spider-Man Pointing",
        "image_path": "templates/spiderman_pointing.jpg",
        "texts": [
            {
                "position": (100, 50),
                "text_template": "Me",
                "font_size": 45,
                "color": (255, 255, 255),
                "stroke_color": (0, 0, 0),
                "stroke_width": 3,
                "max_width": 200,
                "align": "center"
            },
            {
                "position": (100, 100),
                "text_template": "RIZZ SCORE: {score}",
                "font_size": 40,
                "color": (255, 215, 0),  # Gold
                "stroke_color": (0, 0, 0),
                "stroke_width": 2,
                "max_width": 200,
                "align": "center"
            },
            {
                "position": (400, 50),
                "text_template": "The guy she told you not to worry about",
                "font_size": 35,
                "color": (255, 255, 255),
                "stroke_color": (0, 0, 0),
                "stroke_width": 2,
                "max_width": 200,
                "align": "center"
            }
        ],
        "image_size": (600, 500)
    },
    {
        "id": "success_kid",
        "name": "Success Kid",
        "image_path": "templates/success_kid.jpg",
        "texts": [
            {
                "position": (50, 30),
                "text_template": "Got left on read for 3 hours",
                "font_size": 40,
                "color": (255, 255, 255),
                "stroke_color": (0, 0, 0),
                "stroke_width": 2,
                "max_width": 500,
                "align": "left"
            },
            {
                "position": (50, 400),
                "text_template": "Still has a higher Rizz Score than my friend.",
                "font_size": 35,
                "color": (255, 255, 255),
                "stroke_color": (0, 0, 0),
                "stroke_width": 2,
                "max_width": 500,
                "align": "left"
            },
            {
                "position": (300, 200),
                "text_template": "{score}/100",
                "font_size": 50,
                "color": (255, 215, 0),
                "stroke_color": (0, 0, 0),
                "stroke_width": 3,
                "max_width": 200,
                "align": "center"
            }
        ],
        "image_size": (600, 500)
    },
    {
        "id": "doge",
        "name": "Doge",
        "image_path": "templates/doge.jpg",
        "texts": [
            {
                "position": (50, 30),
                "text_template": "wow.",
                "font_size": 35,
                "color": (255, 255, 255),
                "stroke_color": (0, 0, 0),
                "stroke_width": 2,
                "max_width": 150,
                "align": "left"
            },
            {
                "position": (450, 30),
                "text_template": "such rizz.",
                "font_size": 35,
                "color": (255, 255, 255),
                "stroke_color": (0, 0, 0),
                "stroke_width": 2,
                "max_width": 150,
                "align": "right"
            },
            {
                "position": (50, 200),
                "text_template": "very calculate.",
                "font_size": 35,
                "color": (255, 255, 255),
                "stroke_color": (0, 0, 0),
                "stroke_width": 2,
                "max_width": 150,
                "align": "left"
            },
            {
                "position": (450, 200),
                "text_template": "{score}/100.",
                "font_size": 40,
                "color": (255, 215, 0),
                "stroke_color": (0, 0, 0),
                "stroke_width": 3,
                "max_width": 150,
                "align": "right"
            },
            {
                "position": (50, 400),
                "text_template": "much score.",
                "font_size": 35,
                "color": (255, 255, 255),
                "stroke_color": (0, 0, 0),
                "stroke_width": 2,
                "max_width": 150,
                "align": "left"
            },
            {
                "position": (450, 400),
                "text_template": "Amaze.",
                "font_size": 35,
                "color": (255, 255, 255),
                "stroke_color": (0, 0, 0),
                "stroke_width": 2,
                "max_width": 150,
                "align": "right"
            }
        ],
        "image_size": (600, 500)
    }
]


def get_random_template() -> Dict:
    """Get a random meme template from available templates"""
    import os
    
    # Get backend directory to check for template images
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Filter to only templates that have images available
    available_templates = []
    for template in MEME_TEMPLATES:
        template_path = os.path.join(backend_dir, template["image_path"])
        # Check if template image exists
        if os.path.exists(template_path) or os.path.exists(template["image_path"]):
            available_templates.append(template)
    
    # If we have available templates, pick randomly
    if available_templates:
        return random.choice(available_templates)
    
    # Fallback to disaster_girl if no templates found
    print("⚠️ No template images found, using disaster_girl as fallback")
    return get_template_by_id("disaster_girl")


def get_template_by_id(template_id: str) -> Dict:
    """Get a specific template by ID"""
    for template in MEME_TEMPLATES:
        if template["id"] == template_id:
            return template
    return get_random_template()  # Fallback to random if not found

