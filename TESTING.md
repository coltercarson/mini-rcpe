# Testing Guide for mini-rcpe

This project includes a comprehensive unit testing suite built with pytest.

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov/` directory.

### Run Specific Test Files

```bash
# Test CRUD operations
pytest tests/test_crud.py

# Test API endpoints
pytest tests/test_main.py

# Test scraper functionality
pytest tests/test_scraper.py

# Test Pydantic schemas
pytest tests/test_schemas.py
```

### Run Specific Tests

```bash
# Run a specific test class
pytest tests/test_crud.py::TestGetRecipe

# Run a specific test method
pytest tests/test_crud.py::TestGetRecipe::test_get_recipe_exists
```

### Verbose Output

```bash
pytest -v  # Verbose
pytest -vv # Extra verbose
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Pytest fixtures and test configuration
├── test_crud.py          # Tests for database CRUD operations
├── test_main.py          # Tests for FastAPI endpoints
├── test_schemas.py       # Tests for Pydantic models/schemas
└── test_scraper.py       # Tests for recipe scraping functionality
```

## Test Coverage

The test suite covers:

- **CRUD Operations** (crud.py)
  - Creating, reading, updating, and deleting recipes
  - Pagination
  - Cascade deletions
  
- **API Endpoints** (main.py)
  - Authentication (login/logout)
  - Recipe CRUD via REST API
  - Recipe scraping endpoint
  - Image upload
  - Conversions endpoint
  
- **Pydantic Schemas** (schemas.py)
  - Model validation
  - Optional and required fields
  - Nested structures
  
- **Recipe Scraping** (scraper.py)
  - Ingredient parsing with various formats
  - Recipe scraping from URLs
  - Ingredient distribution to steps

## Test Database

Tests use an in-memory SQLite database with `StaticPool` to ensure:
- Fast test execution
- No side effects on the production database
- Clean state for each test
- Proper table creation and cleanup

## Writing New Tests

### Example Test Structure

```python
import pytest
from schemas import RecipeCreate

def test_create_recipe(test_db, sample_recipe_data):
    """Test creating a recipe."""
    recipe = RecipeCreate(**sample_recipe_data)
    # Your test logic here
    assert recipe.title == "Test Recipe"
```

### Available Fixtures

- `test_engine`: Test database engine with in-memory SQLite
- `test_db`: Database session for direct database access
- `client`: TestClient for API endpoint testing
- `authenticated_client`: TestClient with authentication cookie set
- `sample_recipe_data`: Sample recipe data dictionary

## Continuous Integration

Tests are designed to run in CI/CD pipelines. The test suite:
- Completes in under 2 seconds
- Requires no external dependencies (uses mocks for external services)
- Provides clear failure messages
- Generates coverage reports

## Current Coverage

Run `pytest --cov=.` to see current coverage statistics. Target is >90% coverage for all modules.
