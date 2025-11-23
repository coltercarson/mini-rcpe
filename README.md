Online recipes are pretty awful - use this tool to store recipes in a clean and efficient manner with no ads/clutter.

# Features

- **Recipe Scraping**: Automatically extract recipes from thousands of websites using [recipe-scrapers](https://github.com/hhursev/recipe-scraper)
- **LLM Fallback**: When recipe-scrapers fails, automatically fall back to using a local LLM (Ollama) to extract recipe data from unsupported websites
- **Clean Interface**: Store and view recipes without ads or clutter
- **Ingredient Parsing**: Automatically parse ingredients into amounts, units, and names
- **Step-by-Step Instructions**: Organize recipes into clear, numbered steps

For details on the LLM fallback feature, see [docs/LLM-FALLBACK.md](docs/LLM-FALLBACK.md).

# Deployment via Docker
```bash
git clone <your-repo-url> mini-rcpe
cd mini-rcpe
nano docker/docker-compose.yml # edit key values (e.g., database location, user credentials, port)
docker-compose -f docker/docker-compose.yml up -d
```

For detailed Docker deployment instructions, see [docs/README-DOCKER.md](docs/README-DOCKER.md).

# Development

## Running Tests

This project includes comprehensive unit tests. To run the test suite:

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=.
```

See [TESTING.md](TESTING.md) for detailed testing documentation.
