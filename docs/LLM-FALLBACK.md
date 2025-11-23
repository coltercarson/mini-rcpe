# Local LLM Fallback Feature

## Overview

The Local LLM Fallback feature provides an alternative method for extracting recipe information when the primary `recipe-scrapers` library fails to parse a website. This is particularly useful for:

- Websites not supported by recipe-scrapers
- Recipe blogs with non-standard formats
- Sites that block or restrict automated scraping
- Custom recipe formats

## How It Works

1. **Primary Method**: The application first attempts to scrape recipes using the `recipe-scrapers` library
2. **Fallback Trigger**: If recipe-scrapers fails (e.g., unsupported website), the system automatically falls back to the LLM
3. **LLM Processing**: The LLM analyzes the raw HTML/text and extracts recipe information
4. **Output**: The LLM returns structured JSON data in the same format as recipe-scrapers

## Requirements

### Ollama Installation

The LLM fallback feature uses [Ollama](https://ollama.ai/), a local LLM runtime for Linux, macOS, and Windows.

#### Installing Ollama on Linux

```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

#### Starting Ollama Service

```bash
# Start Ollama service
ollama serve
```

The service will run on `http://localhost:11434` by default.

#### Downloading a Model

```bash
# Download the recommended model (llama3.2 - ~2GB)
ollama pull llama3.2

# Or download a smaller model for faster performance (llama3.2:1b - ~1GB)
ollama pull llama3.2:1b

# Or download other models
ollama pull mistral      # ~4GB
ollama pull llama2       # ~4GB
```

## Configuration

### Environment Variables

Add the following variables to your `.env` file:

```bash
# Enable LLM fallback (set to "true" to enable)
LLM_ENABLED=true

# Ollama API endpoint (default: http://localhost:11434)
LLM_BASE_URL=http://localhost:11434

# Model to use for recipe extraction (default: llama3.2)
LLM_MODEL=llama3.2

# Timeout for LLM requests in seconds (default: 120)
LLM_TIMEOUT=120
```

### Docker Configuration

If running in Docker, you need to ensure the container can access your Ollama instance:

#### Option 1: Host Network (Linux only)

```yaml
# docker-compose.yml
services:
  mini-rcpe:
    network_mode: "host"
    environment:
      - LLM_ENABLED=true
      - LLM_BASE_URL=http://localhost:11434
```

#### Option 2: Docker Network

```yaml
# docker-compose.yml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    
  mini-rcpe:
    environment:
      - LLM_ENABLED=true
      - LLM_BASE_URL=http://ollama:11434
    depends_on:
      - ollama

volumes:
  ollama-data:
```

#### Option 3: External Ollama Instance

```yaml
# docker-compose.yml
services:
  mini-rcpe:
    environment:
      - LLM_ENABLED=true
      - LLM_BASE_URL=http://192.168.1.100:11434  # Replace with your Ollama host
```

## Usage

Once configured, the LLM fallback works automatically. No code changes are needed in your application.

### Example Scenario

```python
# User submits a URL that recipe-scrapers doesn't support
POST /api/scrape
{
  "url": "https://unsupported-recipe-blog.com/my-recipe"
}

# Response (extracted by LLM):
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
      "action": "Mix flour, sugar, and cocoa powder",
      "time_minutes": null,
      "ingredients": [
        {"ingredient_name": "flour", "amount": 2.0, "unit": "cups"},
        {"ingredient_name": "sugar", "amount": 1.5, "unit": "cups"},
        {"ingredient_name": "cocoa powder", "amount": 0.75, "unit": "cups"}
      ]
    }
  ]
}
```

## Performance Considerations

- **Model Size**: Smaller models (llama3.2:1b) are faster but **significantly less accurate** at recipe extraction
- **Response Time**: LLM extraction typically takes 10-30 seconds depending on model and hardware
- **Resource Usage**: LLMs require significant CPU/RAM (or GPU if available)
- **Caching**: Consider implementing caching for frequently accessed recipes

### Recommended Models by Use Case

| Model | Size | Speed | Accuracy | Use Case | Notes |
|-------|------|-------|----------|----------|-------|
| llama3.2:1b | ~1GB | Fast | Poor | Testing only | Often misses ingredients/steps |
| llama3.2 | ~2GB | Medium | Good | Production (recommended) | Best balance |
| mistral | ~4GB | Slow | Better | High accuracy needs | Requires more RAM |

**Important**: The 1B model often produces incomplete extractions (missing ingredients, combining all steps into one). For production use, allocate at least 4GB RAM and use the standard `llama3.2` (3B) model.

## Troubleshooting

### LLM Not Working

1. **Check Ollama is running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Verify model is downloaded**:
   ```bash
   ollama list
   ```

3. **Check logs**:
   ```bash
   # Application logs will show LLM attempts
   tail -f /var/log/mini-rcpe.log
   ```

4. **Test Ollama directly**:
   ```bash
   curl http://localhost:11434/api/generate -d '{
     "model": "llama3.2",
     "prompt": "Hello, are you working?",
     "stream": false
   }'
   ```

### Common Issues

- **Connection refused**: Ollama service is not running
- **Model not found**: Model hasn't been downloaded with `ollama pull`
- **Timeout**: Increase `LLM_TIMEOUT` or use a faster model
- **Out of memory**: Use a smaller model or increase system RAM

## Disabling LLM Fallback

To disable the feature and use only recipe-scrapers:

```bash
LLM_ENABLED=false
```

Or remove the environment variable entirely.

## Development

### Testing LLM Fallback

```bash
# Run tests for LLM functionality
pytest tests/test_llm_fallback.py -v

# Run tests for scraper with LLM fallback
pytest tests/test_scraper.py::TestScrapeRecipe::test_llm_fallback_on_scraper_failure -v
```

### Manual Testing

```python
from app.llm_fallback import extract_recipe_with_llm

# Test with sample HTML
html = """
<html>
  <body>
    <h1>My Amazing Recipe</h1>
    <p>Serves 4 | 30 minutes</p>
    <h2>Ingredients</h2>
    <ul>
      <li>2 cups flour</li>
      <li>1 cup sugar</li>
    </ul>
    <h2>Instructions</h2>
    <p>Mix ingredients. Bake at 350°F for 25 minutes.</p>
  </body>
</html>
"""

result = extract_recipe_with_llm(html, "http://example.com")
print(result)
```

## Security Considerations

- The LLM processes untrusted HTML content
- All HTML is sanitized before being sent to the LLM
- The LLM runs locally and doesn't send data to external services
- Rate limiting is recommended for production deployments

## Future Enhancements

Potential improvements for this feature:

- [ ] Support for remote LLM APIs (OpenAI, Anthropic, etc.)
- [ ] Caching of LLM-extracted recipes
- [ ] Confidence scoring for extractions
- [ ] User feedback mechanism to improve accuracy
- [ ] Fine-tuning on recipe-specific datasets
- [ ] GPU acceleration support
