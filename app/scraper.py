from recipe_scrapers import scrape_html
import requests
import os
import uuid
import re
from urllib.parse import urlparse
from typing import Optional
import ipaddress
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Configuration constants
HTTP_TIMEOUT = 30  # Timeout for HTTP requests in seconds

# Import LLM fallback (will gracefully handle if not available)
try:
    from app.llm_fallback import extract_recipe_with_llm
    LLM_AVAILABLE = True
    logger.info("LLM fallback module loaded successfully")
except Exception as e:
    LLM_AVAILABLE = False
    extract_recipe_with_llm = None
    logger.warning(f"LLM fallback not available: {e}")


def is_llm_enabled() -> bool:
    """Check if LLM fallback is enabled and available."""
    enabled = LLM_AVAILABLE and os.getenv("LLM_ENABLED", "false").lower() == "true"
    if not LLM_AVAILABLE:
        logger.debug("LLM not available (import failed)")
    elif not os.getenv("LLM_ENABLED", "false").lower() == "true":
        logger.debug(f"LLM not enabled (LLM_ENABLED={os.getenv('LLM_ENABLED', 'false')})")
    return enabled


def validate_url(url: str) -> None:
    """
    Validate URL to prevent SSRF attacks.
    Raises Exception if URL is invalid or potentially dangerous.
    """
    try:
        parsed = urlparse(url)
        
        # Only allow HTTP and HTTPS
        if parsed.scheme not in ('http', 'https'):
            raise Exception("Only HTTP and HTTPS URLs are allowed")
        
        # Ensure hostname is present
        if not parsed.hostname:
            raise Exception("Invalid URL: no hostname")
        
        # Block requests to private/local IP addresses
        try:
            ip = ipaddress.ip_address(parsed.hostname)
            if ip.is_private or ip.is_loopback or ip.is_reserved:
                raise Exception("Requests to private/local IP addresses are not allowed")
        except ValueError:
            # Hostname is not an IP address, which is fine
            # Additional check: block localhost variants
            if parsed.hostname.lower() in ('localhost', '0.0.0.0', '127.0.0.1', '::1'):
                raise Exception("Requests to localhost are not allowed")
    
    except Exception as e:
        raise Exception(f"Invalid URL: {str(e)}")

def parse_ingredient(ing_str: str) -> dict:
    """Parse an ingredient string into amount, unit, and name."""
    # Common units to look for
    units = [
        'cup', 'cups', 'tablespoon', 'tablespoons', 'tbsp', 'teaspoon', 'teaspoons', 'tsp',
        'ounce', 'ounces', 'oz', 'pound', 'pounds', 'lb', 'lbs',
        'gram', 'grams', 'g', 'kilogram', 'kilograms', 'kg',
        'milliliter', 'milliliters', 'ml', 'liter', 'liters', 'l',
        'pinch', 'dash', 'clove', 'cloves', 'slice', 'slices'
    ]
    
    # Pattern: optional amount (number/fraction) + optional unit + name
    # Examples: "2 cups flour", "500g sugar", "1/2 teaspoon salt", "3 eggs"
    # Use word boundary \b to ensure complete unit match
    pattern = r'^([\d./\s]+)?\s*\b(' + '|'.join(units) + r')\b\s*(.+)$'
    match = re.match(pattern, ing_str.strip(), re.IGNORECASE)
    
    if match:
        amount_str = match.group(1)
        unit = match.group(2)
        name = match.group(3)
        
        # Parse amount (handle fractions like "1/2")
        amount = None
        if amount_str:
            amount_str = amount_str.strip()
            try:
                # Handle fractions
                if '/' in amount_str:
                    parts = amount_str.split('/')
                    if len(parts) == 2:
                        amount = float(parts[0]) / float(parts[1])
                else:
                    amount = float(amount_str)
            except (ValueError, ZeroDivisionError):
                pass
        
        return {
            "ingredient_name": name.strip() if name else ing_str,
            "amount": amount,
            "unit": unit.lower() if unit else None
        }
    
    # If no unit match, try to match just amount and name
    pattern_no_unit = r'^([\d./]+)\s*([a-zA-Z]?)?\s*(.+)$'
    match_no_unit = re.match(pattern_no_unit, ing_str.strip())
    
    if match_no_unit:
        amount_str = match_no_unit.group(1)
        unit_str = match_no_unit.group(2)
        name = match_no_unit.group(3)
        
        # Parse amount
        amount = None
        if amount_str:
            try:
                if '/' in amount_str:
                    parts = amount_str.split('/')
                    if len(parts) == 2:
                        amount = float(parts[0]) / float(parts[1])
                else:
                    amount = float(amount_str)
            except (ValueError, ZeroDivisionError):
                pass
        
        # Check if single letter after number is a unit (g, l, etc)
        unit = None
        if unit_str and unit_str.lower() in ['g', 'l']:
            unit = unit_str.lower()
        else:
            # If not a unit, it's part of the name
            if unit_str:
                name = unit_str + name
        
        return {
            "ingredient_name": name.strip() if name else ing_str,
            "amount": amount,
            "unit": unit
        }
    
    # If no match, return the whole string as name
    return {
        "ingredient_name": ing_str,
        "amount": None,
        "unit": None
    }

def scrape_recipe(url: str, use_llm_fallback: bool = True) -> dict:
    """
    Scrape a recipe from a URL using recipe-scrapers.
    If recipe-scrapers fails and use_llm_fallback is True, attempt to use local LLM.
    
    Args:
        url: URL of the recipe
        use_llm_fallback: Whether to use LLM fallback on failure (default: True)
    
    Returns:
        Dictionary with recipe data
    
    Raises:
        Exception: If both recipe-scrapers and LLM fallback fail
    
    Security:
        URL validation is performed to prevent SSRF attacks. Only HTTP/HTTPS URLs
        to public internet addresses are allowed.
    """
    # Validate URL to prevent SSRF attacks
    # This blocks requests to localhost, private IPs, and non-HTTP(S) schemes
    validate_url(url)
    
    # Add User-Agent to avoid 403/404 on some sites
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Fetch HTML
    try:
        response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        raise Exception(f"Failed to fetch URL: {str(e)}")
    
    # Try recipe-scrapers first
    logger.info(f"Attempting to scrape recipe from: {url}")
    try:
        scraper = scrape_html(html, org_url=url)
        logger.info("Successfully scraped recipe using recipe-scrapers")
    except Exception as scraper_error:
        logger.warning(f"Recipe-scrapers failed: {scraper_error}")
        
        # Check if LLM fallback is available
        llm_enabled = is_llm_enabled()
        logger.info(f"LLM fallback check - use_llm_fallback={use_llm_fallback}, is_llm_enabled={llm_enabled}")
        
        # If recipe-scrapers fails, try LLM fallback
        if use_llm_fallback and llm_enabled:
            logger.info("Attempting LLM fallback...")
            try:
                llm_result = extract_recipe_with_llm(html, url)
                if llm_result:
                    logger.info("Successfully extracted recipe using LLM fallback")
                    return llm_result
                else:
                    logger.error("LLM returned None")
                    raise Exception(f"Both recipe-scrapers and LLM fallback failed. Recipe-scrapers error: {scraper_error}. LLM returned no result.")
            except Exception as llm_error:
                logger.error(f"LLM extraction error: {llm_error}")
                raise Exception(f"Both recipe-scrapers and LLM fallback failed. Recipe-scrapers error: {scraper_error}. LLM error: {llm_error}")
        else:
            # Re-raise original error if LLM not available/enabled
            if not use_llm_fallback:
                logger.info("LLM fallback disabled by parameter")
            elif not llm_enabled:
                logger.info("LLM fallback not enabled or not available")
            raise Exception(f"Recipe extraction failed: {scraper_error}")
    
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
    
    # Distribute ingredients to steps based on keyword matching
    if steps and ingredients:
        # Parse all ingredients first
        parsed_ingredients = [parse_ingredient(ing_str) for ing_str in ingredients]
        
        # Track which ingredients have been assigned
        assigned_ingredients = set()
        
        # For each step, find ingredients mentioned in its action text
        for step in steps:
            action_lower = step["action"].lower()
            
            for idx, parsed_ing in enumerate(parsed_ingredients):
                if idx in assigned_ingredients:
                    continue
                    
                # Extract key words from ingredient name for matching
                ing_name = parsed_ing["ingredient_name"].lower()
                
                # Remove common words and split into keywords
                common_words = {'the', 'a', 'an', 'of', 'to', 'for', 'and', 'or', 'in', 'on', 'with'}
                ing_keywords = [word for word in ing_name.split() if word not in common_words and len(word) > 2]
                
                # Check if any keyword from ingredient appears in the step action
                if any(keyword in action_lower for keyword in ing_keywords):
                    step["ingredients"].append(parsed_ing)
                    assigned_ingredients.add(idx)
        
        # Add any unassigned ingredients to the first step
        for idx, parsed_ing in enumerate(parsed_ingredients):
            if idx not in assigned_ingredients:
                steps[0]["ingredients"].append(parsed_ing)
                
    elif ingredients:
        # If no steps found but ingredients exist, create a dummy step
        steps.append({
            "step_number": 1,
            "action": "Prepare ingredients",
            "time_minutes": None,
            "ingredients": [parse_ingredient(i) for i in ingredients]
        })

    return {
        "title": title,
        "total_time_minutes": total_time,
        "base_servings": base_servings,
        "image_filename": local_image_filename,
        "steps": steps
    }
