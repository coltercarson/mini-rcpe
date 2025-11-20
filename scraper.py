from recipe_scrapers import scrape_html
import requests
import os
import uuid
import re
from urllib.parse import urlparse

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def scrape_recipe(url: str) -> dict:
    # Add User-Agent to avoid 403/404 on some sites
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    html = requests.get(url, headers=headers).text
    scraper = scrape_html(html, org_url=url)
    
    # Extract data
    title = scraper.title()
    total_time = scraper.total_time() # returns int (minutes)
    yields = scraper.yields() # returns string usually
    image_url = scraper.image()
    ingredients = scraper.ingredients()
    instructions = scraper.instructions() # returns string usually
    
    # Parse yields
    base_servings = 1
    if yields:
        match = re.search(r'\d+', yields)
        if match:
            base_servings = int(match.group())
            
    # Image download disabled per user request
    local_image_filename = None

    # Parse instructions
    steps = []
    if isinstance(instructions, str):
        # Split by newlines and filter empty
        raw_steps = [s.strip() for s in instructions.split('\n') if s.strip()]
        for i, action in enumerate(raw_steps):
            steps.append({
                "step_number": i + 1,
                "action": action,
                "time_minutes": None,
                "ingredients": [] 
            })
    
    # Attach all ingredients to the first step for now, 
    # as our model requires ingredients to be in steps.
    # The user can reorganize them in the UI.
    if steps and ingredients:
        # We need to parse ingredient strings into name/amount/unit if possible
        # recipe-scrapers gives raw strings usually.
        # We'll just put the whole string in 'ingredient_name' and leave amount/unit empty
        # or try a very basic split.
        for ing_str in ingredients:
            steps[0]["ingredients"].append({
                "ingredient_name": ing_str,
                "amount": None,
                "unit": None
            })
    elif ingredients:
        # If no steps found but ingredients exist, create a dummy step
        steps.append({
            "step_number": 1,
            "action": "Prepare ingredients",
            "time_minutes": None,
            "ingredients": [{"ingredient_name": i, "amount": None, "unit": None} for i in ingredients]
        })

    return {
        "title": title,
        "total_time_minutes": total_time,
        "base_servings": base_servings,
        "image_filename": local_image_filename,
        "steps": steps
    }
