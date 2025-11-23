"""
Local LLM fallback for recipe extraction when recipe-scrapers fails.
Uses Ollama (or compatible API) to extract recipe data from raw HTML/text.
"""
import os
import re
import json
import requests
from typing import Optional, Dict, Any

# Import with relative import to avoid circular dependencies
try:
    from app.scraper import parse_ingredient
except ImportError:
    from scraper import parse_ingredient


# Configuration constants
MAX_TEXT_LENGTH = 8000  # Maximum text length to send to LLM (to stay within context limits)


def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration from environment variables."""
    return {
        "base_url": os.getenv("LLM_BASE_URL", "http://localhost:11434"),
        "model": os.getenv("LLM_MODEL", "llama3.2"),
        "timeout": int(os.getenv("LLM_TIMEOUT", "120")),
    }


def clean_html_to_text(html: str) -> str:
    """
    Extract plain text from HTML, removing scripts, styles, and excessive whitespace.
    
    Note: This is a best-effort HTML cleaning for preparing text to send to an LLM.
    It's not a security-critical HTML sanitizer. The LLM processes the text in isolation
    and doesn't execute any code, so perfect HTML parsing is not required.
    """
    # Remove script and style elements (handles most common cases)
    # Note: This regex-based approach is not perfect for all edge cases with malformed HTML,
    # but it's sufficient for cleaning recipe HTML before LLM processing
    text = re.sub(r'<script[^>]*>.*?</script\s*>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style\s*>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Decode common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def extract_recipe_with_llm(html_or_text: str, url: str) -> Optional[Dict[str, Any]]:
    """
    Use a local LLM to extract recipe information from HTML or text.
    
    Args:
        html_or_text: Raw HTML or text containing recipe information
        url: Original URL (for reference)
    
    Returns:
        Dictionary with recipe data in the same format as scraper.scrape_recipe()
        or None if LLM extraction fails
    """
    config = get_llm_config()
    
    # Clean HTML to text if needed
    if '<html' in html_or_text.lower() or '<body' in html_or_text.lower():
        text = clean_html_to_text(html_or_text)
    else:
        text = html_or_text
    
    # Truncate text if too long (keep first MAX_TEXT_LENGTH chars to stay within context limits)
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH] + "..."
    
    # Create prompt for the LLM
    prompt = f"""Extract the recipe information from the following text and return it as a JSON object with this exact structure:
{{
  "title": "Recipe Title",
  "total_time_minutes": 30,
  "base_servings": 4,
  "ingredients": ["ingredient 1", "ingredient 2"],
  "instructions": "Step 1. Do this.\\nStep 2. Do that."
}}

Guidelines:
- Extract the recipe title
- Extract total cooking/preparation time in minutes (null if not found)
- Extract number of servings (default to 1 if not found)
- List all ingredients as strings (with amounts and units if present)
- Combine all cooking instructions into a single string, separated by newlines
- Return ONLY the JSON object, no other text
- If you cannot find recipe information, return null

Recipe text:
{text}

JSON:"""
    
    try:
        # Call Ollama API
        response = requests.post(
            f"{config['base_url']}/api/generate",
            json={
                "model": config["model"],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for more consistent output
                    "num_predict": 2000,  # Limit response length
                }
            },
            timeout=config["timeout"]
        )
        
        if response.status_code != 200:
            print(f"LLM API error: {response.status_code} - {response.text}")
            return None
        
        result = response.json()
        llm_output = result.get("response", "").strip()
        
        # Parse the LLM's JSON response
        recipe_data = parse_llm_response(llm_output)
        
        if recipe_data:
            return recipe_data
        else:
            print(f"Failed to parse LLM response: {llm_output[:200]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"LLM request failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in LLM extraction: {e}")
        return None


def parse_llm_response(llm_output: str) -> Optional[Dict[str, Any]]:
    """
    Parse the LLM's JSON response and convert it to the expected format.
    
    Args:
        llm_output: Raw text output from LLM
    
    Returns:
        Dictionary with recipe data in scraper.scrape_recipe() format
        or None if parsing fails
    """
    try:
        # Try to extract JSON from the response (in case LLM added extra text)
        json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = llm_output
        
        # Parse JSON
        llm_data = json.loads(json_str)
        
        # Check if LLM returned null (couldn't extract recipe)
        if llm_data is None:
            return None
        
        # Extract basic fields
        title = llm_data.get("title", "Untitled Recipe")
        total_time = llm_data.get("total_time_minutes")
        base_servings = llm_data.get("base_servings", 1)
        ingredients = llm_data.get("ingredients", [])
        instructions = llm_data.get("instructions", "")
        
        # Parse instructions into steps
        steps = []
        if instructions:
            raw_steps = [s.strip() for s in instructions.split('\n') if s.strip()]
            for i, action in enumerate(raw_steps):
                # Remove step numbers if present (e.g., "1.", "Step 1:", etc.)
                action = re.sub(r'^(\d+\.|\d+\)|\bStep\s+\d+:?)\s*', '', action, flags=re.IGNORECASE)
                steps.append({
                    "step_number": i + 1,
                    "action": action,
                    "time_minutes": None,
                    "ingredients": []
                })
        
        # Distribute ingredients to steps based on keyword matching (same logic as scraper.py)
        if steps and ingredients:
            parsed_ingredients = [parse_ingredient(ing_str) for ing_str in ingredients]
            assigned_ingredients = set()
            
            for step in steps:
                action_lower = step["action"].lower()
                
                for idx, parsed_ing in enumerate(parsed_ingredients):
                    if idx in assigned_ingredients:
                        continue
                    
                    ing_name = parsed_ing["ingredient_name"].lower()
                    common_words = {'the', 'a', 'an', 'of', 'to', 'for', 'and', 'or', 'in', 'on', 'with'}
                    ing_keywords = [word for word in ing_name.split() if word not in common_words and len(word) > 2]
                    
                    if any(keyword in action_lower for keyword in ing_keywords):
                        step["ingredients"].append(parsed_ing)
                        assigned_ingredients.add(idx)
            
            # Add unassigned ingredients to first step
            for idx, parsed_ing in enumerate(parsed_ingredients):
                if idx not in assigned_ingredients:
                    steps[0]["ingredients"].append(parsed_ing)
        
        elif ingredients:
            # If no steps but have ingredients, create a dummy step
            steps.append({
                "step_number": 1,
                "action": "Prepare ingredients",
                "time_minutes": None,
                "ingredients": [parse_ingredient(i) for i in ingredients]
            })
        
        # Return in the same format as scraper.scrape_recipe()
        return {
            "title": title,
            "total_time_minutes": total_time,
            "base_servings": base_servings,
            "image_filename": None,
            "steps": steps
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return None
