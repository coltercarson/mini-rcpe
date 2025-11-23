# LLM Fallback Feature - Quick Start Guide

This guide demonstrates how to use the LLM fallback feature for recipe extraction.

## Prerequisites

1. **Install Ollama** (if you want to use the LLM fallback):
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

2. **Download a model**:
```bash
ollama pull llama3.2
```

3. **Start Ollama**:
```bash
ollama serve
```

## Configuration

Edit your `.env` file or set environment variables:

```bash
# Enable LLM fallback
LLM_ENABLED=true

# Configure Ollama endpoint (default shown)
LLM_BASE_URL=http://localhost:11434

# Choose model (smaller = faster, larger = more accurate)
LLM_MODEL=llama3.2

# Request timeout in seconds
LLM_TIMEOUT=120
```

## How It Works

### Scenario 1: Supported Website
When you submit a URL from a supported recipe site (e.g., AllRecipes, Food Network):
1. The app uses `recipe-scrapers` library
2. Recipe is extracted instantly
3. LLM is not used

### Scenario 2: Unsupported Website (LLM Enabled)
When you submit a URL from an unsupported site:
1. `recipe-scrapers` fails
2. App automatically falls back to LLM
3. LLM analyzes the raw HTML
4. Recipe is extracted (takes 10-30 seconds)
5. Result is returned in the same format

### Scenario 3: Unsupported Website (LLM Disabled)
When you submit a URL from an unsupported site and LLM is disabled:
1. `recipe-scrapers` fails
2. Error is returned to user
3. Recipe cannot be extracted

## Example API Usage

```bash
# Scrape a recipe (will use LLM fallback if needed)
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example-recipe-blog.com/my-recipe"}'

# Response format (same whether from recipe-scrapers or LLM):
{
  "title": "Delicious Chocolate Cake",
  "total_time_minutes": 60,
  "base_servings": 8,
  "image_filename": null,
  "steps": [
    {
      "step_number": 1,
      "action": "Preheat oven to 350°F",
      "time_minutes": null,
      "ingredients": []
    },
    {
      "step_number": 2,
      "action": "Mix flour, sugar, and cocoa powder in a bowl",
      "time_minutes": null,
      "ingredients": [
        {
          "ingredient_name": "flour",
          "amount": 2.0,
          "unit": "cups"
        },
        {
          "ingredient_name": "sugar",
          "amount": 1.5,
          "unit": "cups"
        }
      ]
    }
  ]
}
```

## Testing the Feature

### 1. Test URL Validation (Security)
```python
from app.scraper import validate_url

# These should work:
validate_url("https://www.allrecipes.com/recipe/123/")
validate_url("http://example.com/recipe")

# These should raise exceptions:
validate_url("http://localhost:8080/")  # Blocked: localhost
validate_url("http://192.168.1.1/")     # Blocked: private IP
validate_url("file:///etc/passwd")      # Blocked: non-HTTP protocol
```

### 2. Test HTML Cleaning
```python
from app.llm_fallback import clean_html_to_text

html = """
<html>
  <script>alert('test');</script>
  <h1>My Recipe</h1>
  <p>Ingredients: flour, sugar, eggs</p>
</html>
"""

clean_text = clean_html_to_text(html)
# Result: "My Recipe Ingredients: flour, sugar, eggs"
# Note: <script> tags are removed
```

### 3. Test LLM Response Parsing
```python
from app.llm_fallback import parse_llm_response
import json

llm_response = {
    "title": "Test Recipe",
    "total_time_minutes": 30,
    "base_servings": 4,
    "ingredients": ["2 cups flour", "1 cup water"],
    "instructions": "Mix ingredients.\nBake for 20 minutes."
}

result = parse_llm_response(json.dumps(llm_response))
# Result: Properly formatted recipe dict with steps and ingredients
```

## Performance Tips

1. **Use a smaller model for development**:
   ```bash
   ollama pull llama3.2:1b  # Faster, ~1GB
   ```

2. **Use a larger model for production**:
   ```bash
   ollama pull mistral  # More accurate, ~4GB
   ```

3. **Adjust timeout based on your hardware**:
   ```bash
   LLM_TIMEOUT=180  # 3 minutes for slower machines
   ```

4. **Consider caching frequently accessed recipes** (not implemented yet, but recommended)

## Troubleshooting

### Issue: "LLM request failed: Connection refused"
**Solution**: Make sure Ollama is running:
```bash
ollama serve
```

### Issue: "Model not found"
**Solution**: Download the model:
```bash
ollama pull llama3.2
```

### Issue: "Request timed out"
**Solution**: Increase timeout or use a smaller model:
```bash
LLM_TIMEOUT=180
LLM_MODEL=llama3.2:1b
```

### Issue: LLM returns incomplete/incorrect data
**Solution**: 
1. Try a larger/better model (e.g., mistral)
2. Check the source website HTML is reasonable
3. Look at app logs to see what the LLM returned

## Monitoring

When LLM fallback is triggered, you'll see messages in the application logs:

```
Recipe-scrapers failed: WebsiteNotSupported. Attempting LLM fallback...
Successfully extracted recipe using LLM fallback
```

## Disabling the Feature

To disable LLM fallback and use only `recipe-scrapers`:

```bash
LLM_ENABLED=false
```

Or remove the environment variable entirely.

## Notes

- The LLM runs **locally** on your server - no data is sent to external services
- First LLM request may be slower as the model loads into memory
- Subsequent requests to the same model are faster
- LLM extraction takes ~10-30 seconds vs ~1 second for recipe-scrapers
- The feature is completely optional and disabled by default

## Further Reading

- Full documentation: [docs/LLM-FALLBACK.md](../docs/LLM-FALLBACK.md)
- Ollama documentation: https://ollama.ai/
- Available models: https://ollama.ai/library
