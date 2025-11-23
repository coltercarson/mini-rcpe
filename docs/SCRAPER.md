# Recipe Scraper Documentation

The recipe scraper extracts structured recipe data from external websites and converts it into a format compatible with Mini-RCPE's database.

## Overview

Mini-RCPE uses the [`recipe-scrapers`](https://github.com/hhursev/recipe-scrapers) library to extract recipe information from over 250+ recipe websites. The scraper parses ingredients, instructions, and metadata into a structured format.

## API Endpoint

### POST `/api/scrape`

Scrapes a recipe from a given URL and returns structured data.

**Request Body:**
```json
{
  "url": "https://example.com/recipe-page"
}
```

**Response:**
```json
{
  "title": "Chocolate Chip Cookies",
  "total_time_minutes": 30,
  "base_servings": 24,
  "image_filename": null,
  "steps": [
    {
      "step_number": 1,
      "action": "Preheat oven to 375°F",
      "time_minutes": null,
      "ingredients": []
    },
    {
      "step_number": 2,
      "action": "Mix butter and sugar until fluffy",
      "time_minutes": null,
      "ingredients": [
        {
          "ingredient_name": "butter",
          "amount": 1,
          "unit": "cup"
        },
        {
          "ingredient_name": "sugar",
          "amount": 0.75,
          "unit": "cup"
        }
      ]
    }
  ]
}
```

## Core Functions

### `scrape_recipe(url: str) -> dict`

Main scraping function that orchestrates the entire extraction process.

**Parameters:**
- `url` (str): The URL of the recipe page to scrape

**Returns:**
- Dictionary containing recipe data with the following structure:
  - `title` (str): Recipe name
  - `total_time_minutes` (int): Total preparation and cooking time
  - `base_servings` (int): Number of servings the recipe yields
  - `image_filename` (str | None): Local filename of downloaded image (currently disabled)
  - `steps` (list): Array of instruction steps with associated ingredients

**Example:**
```python
from app.scraper import scrape_recipe

data = scrape_recipe("https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/")
print(data["title"])  # "Best Chocolate Chip Cookies"
```

**Error Handling:**
- Raises `requests.exceptions.RequestException` if URL cannot be fetched
- Raises exceptions from `recipe-scrapers` library for parsing errors

---

### `parse_ingredient(ing_str: str) -> dict`

Parses a raw ingredient string into structured components: amount, unit, and name.

**Parameters:**
- `ing_str` (str): Raw ingredient string (e.g., "2 cups flour", "500g sugar", "3 eggs")

**Returns:**
- Dictionary with keys:
  - `ingredient_name` (str): The ingredient name
  - `amount` (float | None): Numeric quantity
  - `unit` (str | None): Unit of measurement

**Examples:**

```python
from app.scraper import parse_ingredient

# With amount and unit
parse_ingredient("2 cups flour")
# Returns: {"ingredient_name": "flour", "amount": 2.0, "unit": "cup"}

# Fraction support
parse_ingredient("1/2 teaspoon salt")
# Returns: {"ingredient_name": "salt", "amount": 0.5, "unit": "teaspoon"}

# Metric units
parse_ingredient("500g sugar")
# Returns: {"ingredient_name": "sugar", "amount": 500.0, "unit": "g"}

# No unit
parse_ingredient("3 eggs")
# Returns: {"ingredient_name": "eggs", "amount": 3.0, "unit": None}

# Complex strings
parse_ingredient("1 tablespoon vanilla extract")
# Returns: {"ingredient_name": "vanilla extract", "amount": 1.0, "unit": "tablespoon"}
```

**Supported Units:**
- Volume: cup, tablespoon (tbsp), teaspoon (tsp), milliliter (ml), liter (l)
- Weight: ounce (oz), pound (lb/lbs), gram (g), kilogram (kg)
- Other: pinch, dash, clove, slice

**Pattern Matching:**
1. Attempts to match: `[amount] [unit] [name]`
2. Falls back to: `[amount] [name]` (no unit)
3. If no match, returns entire string as `ingredient_name`

---

## How It Works

### 1. URL Fetching

The scraper fetches HTML content with a custom User-Agent header to avoid 403 errors from recipe sites:

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
html = requests.get(url, headers=headers).text
```

### 2. Data Extraction

Uses `recipe-scrapers` library to extract:
- Recipe title
- Total time (in minutes)
- Yield/servings (parsed to extract numeric value)
- Image URL (downloading currently disabled)
- Ingredients (list of strings)
- Instructions (text block)

### 3. Instruction Parsing

Instructions are split into individual steps:
- Splits by newlines
- Filters empty lines
- Assigns sequential step numbers
- Creates step objects with action text

### 4. Ingredient Distribution

**Intelligent ingredient assignment to steps:**

For each step, the scraper:
1. Parses all ingredients using `parse_ingredient()`
2. Extracts keywords from each ingredient name
3. Searches for those keywords in the step's action text
4. Assigns matching ingredients to that step
5. Any unassigned ingredients go to Step 1

**Example:**

```
Step 2: "Mix butter and sugar until fluffy"
Ingredients: ["1 cup butter", "3/4 cup sugar", "2 eggs", "2 cups flour"]

Result:
- Step 2 gets: butter, sugar (keywords match)
- Step 1 gets: eggs, flour (unassigned fallback)
```

This creates a more intuitive experience where ingredients appear alongside the step where they're used.

---

## Configuration

### Upload Directory

Images are saved to:
```python
UPLOAD_DIR = "app/static/uploads"
```

The directory is created automatically if it doesn't exist.

### Image Downloading

Currently **disabled** per user request. To enable:

```python
# In scrape_recipe() function, uncomment:
local_image_filename = None
if image_url:
    img_response = requests.get(image_url, headers=headers)
    ext = os.path.splitext(urlparse(image_url).path)[1] or '.jpg'
    local_image_filename = f"{uuid.uuid4()}{ext}"
    with open(os.path.join(UPLOAD_DIR, local_image_filename), 'wb') as f:
        f.write(img_response.content)
```

---

## Supported Websites

The scraper supports 250+ recipe websites through the `recipe-scrapers` library, including:

- AllRecipes.com
- Food Network
- BBC Good Food
- NYT Cooking
- Serious Eats
- Bon Appétit
- Many more...

Full list: [recipe-scrapers GitHub](https://github.com/hhursev/recipe-scrapers#scrapers-available-for)

---

## Error Scenarios

### Common Issues

**403 Forbidden:**
- Solution: User-Agent header is included to mimic browser requests

**Unsupported Website:**
- The site isn't in the `recipe-scrapers` database
- Scraper will raise an exception
- Users should manually enter the recipe

**Malformed HTML:**
- Some sites may have non-standard recipe markup
- Scraper may return incomplete data

**No Ingredients Found:**
- Falls back to creating a single step: "Prepare ingredients"

---

## Testing

See test coverage in [`tests/test_scraper.py`](../tests/test_scraper.py):

```bash
# Run scraper tests
pytest tests/test_scraper.py -v

# Test with coverage
pytest tests/test_scraper.py --cov=app.scraper
```

**Test cases include:**
- Ingredient parsing with various formats
- Fraction handling (1/2, 1/4, etc.)
- Unit recognition (metric and imperial)
- Edge cases (no amount, no unit, complex strings)
- End-to-end scraping from real websites

---

## Usage in Application

### Frontend Integration

Users enter a URL in the recipe form:

```html
<input type="url" name="scrape_url" placeholder="Paste recipe URL">
<button type="button" onclick="scrapeRecipe()">Import</button>
```

JavaScript makes the API call:

```javascript
async function scrapeRecipe() {
  const url = document.querySelector('input[name="scrape_url"]').value;
  
  const response = await fetch('/api/scrape', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  
  const data = await response.json();
  // Populate form with scraped data
  populateForm(data);
}
```

### Backend Flow

```
User submits URL
    ↓
POST /api/scrape
    ↓
scraper.scrape_recipe(url)
    ↓
Parse ingredients & instructions
    ↓
Return structured JSON
    ↓
Frontend populates form
    ↓
User reviews/edits
    ↓
POST to /recipes/new
    ↓
Save to database
```

---

## Performance Considerations

- **Network latency:** Fetching external URLs adds 1-3 seconds
- **Parsing time:** Ingredient distribution is O(n×m) where n=steps, m=ingredients
- **No caching:** Each scrape fetches fresh data (no duplicate detection)

---

## Future Enhancements

Potential improvements:

1. **Caching:** Store scraped recipes to avoid re-fetching
2. **Image support:** Re-enable image downloading with optimization
3. **Nutrition data:** Extract calories/macros if available
4. **Better ingredient matching:** Use fuzzy matching or NLP
5. **User feedback:** Allow manual ingredient reassignment to steps
6. **Batch scraping:** Support multiple URLs at once
7. **Recipe deduplication:** Check if URL already exists in database

---

## Dependencies

```
recipe-scrapers>=14.0.0
requests>=2.31.0
```

Install with:
```bash
pip install recipe-scrapers requests
```

---

## Related Documentation

- [API Reference](API.md) - Full endpoint documentation
- [Testing Guide](../tests/TESTING.md) - How to test scraper functionality
- [Data Models](MODELS.md) - Database schema for recipes
