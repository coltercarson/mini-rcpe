# GitHub Copilot Instructions for mini-rcpe

This document provides instructions for GitHub Copilot when working with the mini-rcpe repository.

## Project Overview

mini-rcpe is a clean recipe management tool that scrapes recipes from websites and stores them without ads or clutter. Key features include:
- Automatic recipe scraping using recipe-scrapers library
- LLM fallback for unsupported websites using Ollama
- Clean web interface for recipe storage and viewing
- Ingredient parsing and step-by-step instructions
- Image upload support

## Tech Stack

- **Framework**: FastAPI (Python web framework)
- **Database**: SQLAlchemy with SQLite
- **Validation**: Pydantic schemas
- **Templates**: Jinja2
- **Testing**: pytest with pytest-cov, pytest-asyncio, httpx
- **Scraping**: recipe-scrapers library
- **LLM Integration**: Ollama for fallback extraction

## Project Structure

```
mini-rcpe/
├── app/                    # Main application package
│   ├── main.py            # FastAPI application and routes
│   ├── models.py          # SQLAlchemy database models
│   ├── database.py        # Database connection management
│   ├── crud.py            # CRUD operations
│   ├── schemas.py         # Pydantic validation schemas
│   ├── scraper.py         # Recipe scraping logic
│   ├── llm_fallback.py    # LLM-based extraction fallback
│   ├── static/            # CSS and uploaded images
│   └── templates/         # Jinja2 HTML templates
├── tests/                 # Comprehensive test suite
├── docs/                  # Project documentation
└── docker/                # Docker deployment files
```

## Development Setup

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Configure environment
cp .env.example .env
# Edit .env to set ADMIN_PASSWORD, DB_PATH, and LLM settings
```

### Running Locally

```bash
# macOS/Linux
./run-dev.sh

# Windows PowerShell
.\run-dev.ps1

# Or directly with uvicorn
uvicorn app.main:app --reload
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_crud.py

# Run with verbose output
pytest -v
```

## Code Style and Conventions

### Python Conventions
- Follow PEP 8 style guidelines
- Use type hints where applicable
- Keep functions focused and single-purpose
- Document complex logic with comments

### Import Organization
- Use absolute imports from the app package:
  ```python
  from app import models, crud, schemas, scraper
  from app.database import engine, get_db
  ```

### Database Patterns
- Use SQLAlchemy ORM for all database operations
- Database operations should go in `app/crud.py`
- Use Pydantic schemas for validation
- Always use database sessions from `get_db()` dependency

### API Patterns
- FastAPI endpoints should be in `app/main.py`
- Use Pydantic schemas for request/response validation
- Return appropriate HTTP status codes
- Handle exceptions with HTTPException

## Testing Guidelines

### Test Structure
- Tests are located in `tests/` directory
- Use pytest fixtures from `conftest.py`
- Each module has a corresponding test file (e.g., `crud.py` → `test_crud.py`)

### Available Fixtures
- `test_engine`: In-memory SQLite database engine
- `test_db`: Database session for testing
- `client`: TestClient for API endpoint testing
- `authenticated_client`: Pre-authenticated TestClient
- `sample_recipe_data`: Sample recipe data dictionary

### Writing Tests
- Use descriptive test names: `test_<action>_<scenario>`
- Group related tests in classes: `class TestGetRecipe:`
- Test both success and failure cases
- Mock external dependencies (e.g., recipe-scrapers, Ollama)
- Aim for >90% code coverage

### Test Examples

```python
def test_create_recipe(test_db, sample_recipe_data):
    """Test creating a recipe in the database."""
    recipe = crud.create_recipe(test_db, sample_recipe_data)
    assert recipe.title == sample_recipe_data["title"]

def test_api_endpoint(client):
    """Test API endpoint with TestClient."""
    response = client.get("/api/recipes")
    assert response.status_code == 200
```

## Common Tasks

### Adding a New Endpoint
1. Define Pydantic schema in `app/schemas.py`
2. Add CRUD operation in `app/crud.py` if needed
3. Create route handler in `app/main.py`
4. Add tests in `tests/test_main.py`

### Adding a Database Model
1. Define model in `app/models.py` using SQLAlchemy
2. Create corresponding Pydantic schema in `app/schemas.py`
3. Add CRUD operations in `app/crud.py`
4. Write tests in `tests/test_crud.py`

### Modifying Scraper Logic
1. Update `app/scraper.py`
2. Update tests in `tests/test_scraper.py`
3. Mock external recipe-scrapers calls in tests
4. Ensure fallback to LLM is handled properly

## Configuration

Environment variables are defined in `.env`:
- `ADMIN_PASSWORD`: Password for recipe editing (required)
- `DB_PATH`: Database file location (default: ./rcpe.db in development, /app/data/rcpe.db in Docker)
- `APP_PORT`: Application port (default: 8000)
- `LLM_ENABLED`: Enable LLM fallback (default: false)
- `LLM_BASE_URL`: Ollama API endpoint (default: http://localhost:11434)
- `LLM_MODEL`: Model name for extraction (default: llama3.2)
- `LLM_TIMEOUT`: LLM request timeout in seconds (default: 120)

## Documentation

Key documentation files:
- `README.md`: Main project documentation
- `docs/STRUCTURE.md`: Detailed repository structure
- `docs/TESTING.md`: Comprehensive testing guide
- `docs/LLM-FALLBACK.md`: LLM fallback feature documentation
- `docs/SCRAPER.md`: Recipe scraper documentation

## CI/CD

GitHub Actions workflow runs on push/PR to main:
- Sets up Python 3.12
- Installs dependencies
- Runs pytest test suite

Tests must pass before merging to main.

## Best Practices

1. **Always run tests** before committing changes
2. **Keep changes focused** - one feature or fix per commit
3. **Update tests** when changing functionality
4. **Document complex logic** with comments
5. **Use type hints** for better code clarity
6. **Handle errors gracefully** with try/except and HTTPException
7. **Mock external services** in tests (recipe-scrapers, Ollama API)
8. **Follow existing patterns** in the codebase
9. **Update documentation** when adding features
10. **Test with coverage** to ensure comprehensive testing
