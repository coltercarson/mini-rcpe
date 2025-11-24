"""
Local LLM fallback for recipe extraction when recipe-scrapers fails.
Uses Ollama (or compatible API) to extract recipe data from raw HTML/text.
"""
import os
import re
import json
import logging
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

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
    from ollama import Client
    
    config = get_llm_config()
    
    # Clean HTML to text if needed
    if '<html' in html_or_text.lower() or '<body' in html_or_text.lower():
        text = clean_html_to_text(html_or_text)
    else:
        text = html_or_text
    
    # Truncate text if too long (keep first MAX_TEXT_LENGTH chars to stay within context limits)
    original_length = len(text)
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH] + "..."
        logger.info(f"Text truncated from {original_length} to {MAX_TEXT_LENGTH} chars")
    else:
        logger.info(f"Sending {original_length} chars to LLM")
    
    # Create prompt for the LLM
    prompt = f"""You are a recipe extraction assistant. Read the following recipe text and extract the recipe information.

IMPORTANT: Do NOT use the example values. Extract the ACTUAL recipe information from the text below.

Return a JSON object with this structure:
{{
  "title": "actual recipe title from the text",
  "total_time_minutes": actual_number_or_null,
  "base_servings": actual_number,
  "steps": [
    {{
      "action": "Step 1 instruction text",
      "time_minutes": number_or_null,
      "ingredients": ["ingredient 1 for this step", "ingredient 2 for this step"]
    }},
    {{
      "action": "Step 2 instruction text",
      "time_minutes": number_or_null,
      "ingredients": ["ingredient 1 for this step"]
    }}
  ]
}}

Requirements:
1. Extract the REAL recipe title from the text
2. Find the total time in minutes (or null if not mentioned)
3. Find how many servings (or use 1 if not mentioned)
4. Create a "steps" array where each step has:
   - "action": The instruction text for this step
   - "time_minutes": Duration for THIS SPECIFIC STEP if mentioned (e.g., "cook for 10 minutes"), otherwise null
   - "ingredients": List of ingredients used in THIS SPECIFIC STEP only
5. Match ingredients to the step where they are actually used
6. If all ingredients are listed together, distribute them intelligently based on when they appear in instructions
7. Return ONLY valid JSON, no extra text before or after
8. If no recipe found, return: null

Recipe text to extract from:
{text}

JSON output:"""
    
    try:
        logger.info(f"Calling LLM API at {config['base_url']} with model {config['model']}")
        if "1b" in config['model'].lower():
            logger.warning("Using 1B model - results may be less accurate. Consider using llama3.2 (3B) or larger for better extraction.")
        
        # Initialize Ollama client
        client = Client(host=config['base_url'])
        
        # Call Ollama using the client library
        response = client.generate(
            model=config["model"],
            prompt=prompt,
            options={
                "temperature": 0.1,  # Low temperature for more consistent output
                "num_predict": 3000,  # Limit response length
                "num_ctx": 4096,  # Context window size
            }
        )
        
        logger.info("LLM API call successful, parsing response...")
        llm_output = response.get("response", "").strip()
        
        # Log the raw LLM output for debugging
        logger.debug(f"Raw LLM output: {llm_output[:500]}...")
        
        # Parse the LLM's JSON response
        recipe_data = parse_llm_response(llm_output)
        
        if recipe_data:
            logger.info(f"Successfully parsed recipe: {recipe_data.get('title', 'Unknown')}")
            return recipe_data
        else:
            logger.error(f"Failed to parse LLM response: {llm_output[:200]}...")
            return None
            
    except Exception as e:
        logger.error(f"LLM request failed: {e}")
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
    # Import here to avoid circular dependency
    from app.scraper import parse_ingredient
    
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
        
        # Parse steps - new format has steps directly in the response
        steps = []
        llm_steps = llm_data.get("steps", [])
        
        if llm_steps and isinstance(llm_steps, list):
            # New format: steps with ingredients and times already structured
            for i, step_data in enumerate(llm_steps):
                if isinstance(step_data, dict):
                    action = step_data.get("action", "").strip()
                    if not action:
                        continue
                    
                    # Remove step numbers if present
                    action = re.sub(r'^(\d+\.|\d+\)|\bStep\s+\d+:?)\s*', '', action, flags=re.IGNORECASE)
                    
                    # Get time for this specific step
                    step_time = step_data.get("time_minutes")
                    
                    # Parse ingredients for this step
                    step_ingredients = []
                    ing_list = step_data.get("ingredients", [])
                    if isinstance(ing_list, list):
                        step_ingredients = [parse_ingredient(ing_str) for ing_str in ing_list if ing_str]
                    
                    steps.append({
                        "step_number": i + 1,
                        "action": action,
                        "time_minutes": step_time,
                        "ingredients": step_ingredients
                    })
        else:
            # Fallback: old format with separate ingredients and instructions
            ingredients = llm_data.get("ingredients", [[]])
            instructions = llm_data.get("instructions", "")
            
            if instructions:
                raw_steps = [s.strip() for s in instructions.split('\n') if s.strip()]
                for i, action in enumerate(raw_steps):
                    action = re.sub(r'^(\d+\.|\d+\)|\bStep\s+\d+:?)\s*', '', action, flags=re.IGNORECASE)
                    
                    # Try to extract time from the action text
                    time_match = re.search(r'(\d+)\s*(?:minute|min|hour|hr)', action, re.IGNORECASE)
                    step_time = None
                    if time_match:
                        time_val = int(time_match.group(1))
                        if 'hour' in action.lower() or 'hr' in action.lower():
                            step_time = time_val * 60
                        else:
                            step_time = time_val
                    
                    # Get ingredients for this step
                    step_ingredients = []
                    if isinstance(ingredients, list) and len(ingredients) > i:
                        step_ing_list = ingredients[i] if isinstance(ingredients[i], list) else []
                        step_ingredients = [parse_ingredient(ing_str) for ing_str in step_ing_list if ing_str]
                    
                    steps.append({
                        "step_number": i + 1,
                        "action": action,
                        "time_minutes": step_time,
                        "ingredients": step_ingredients
                    })
        
        # Return in the same format as scraper.scrape_recipe()
        return {
            "title": title,
            "total_time_minutes": total_time,
            "base_servings": base_servings,
            "image_filename": None,
            "source_url": None,  # Will be set by caller
            "steps": steps
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        logger.debug(f"Failed JSON: {llm_output[:500]}")
        return None
    except Exception as e:
        logger.error(f"Error parsing LLM response: {e}")
        return None
