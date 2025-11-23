# Repository Structure

This document describes the organization of the mini-rcpe codebase.

## Directory Layout

```
mini-rcpe/
├── app/                    # Main application package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # FastAPI application entry point
│   ├── models.py          # SQLAlchemy database models
│   ├── database.py        # Database connection and session management
│   ├── crud.py            # CRUD operations for recipes
│   ├── schemas.py         # Pydantic schemas for validation
│   ├── scraper.py         # Recipe scraping functionality
│   ├── static/            # Static assets (CSS, uploads)
│   │   ├── style.css      # Application styles
│   │   └── uploads/       # User-uploaded images
│   └── templates/         # Jinja2 HTML templates
│       ├── base.html      # Base template
│       ├── index.html     # Recipe list page
│       ├── detail.html    # Recipe detail page
│       ├── form.html      # Recipe creation/edit form
│       └── login.html     # Login page
│
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Test configuration and fixtures
│   ├── test_crud.py       # CRUD operation tests
│   ├── test_main.py       # FastAPI endpoint tests
│   ├── test_schemas.py    # Schema validation tests
│   ├── test_scraper.py    # Scraper tests
│   ├── test_scrape.py     # Legacy scraper tests
│   ├── test_multi_recipe.py
│   └── test_ingredient_distribution.py
│
├── docker/                # Docker configuration
│   ├── Dockerfile         # Container build configuration
│   ├── docker-compose.yml # Multi-container deployment
│   ├── .dockerignore      # Docker ignore rules
│   └── deploy.sh          # Deployment helper script
│
├── docs/                  # Documentation
│   ├── README-DOCKER.md   # Docker deployment guide
│   └── STRUCTURE.md       # This file
│
├── README.md              # Main documentation
├── TESTING.md             # Testing documentation
├── requirements.txt       # Python dependencies
├── requirements-test.txt  # Test dependencies
├── pytest.ini             # Pytest configuration
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
└── mini-rcpe-overview.md  # Project design document
```

## Running the Application

### Local Development
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker
```bash
docker-compose up -d
```

### Running Tests
```bash
# Run a specific test
PYTHONPATH=. python tests/test_scrape.py

# With pytest (if installed)
pytest tests/
```

## Key Files

- **app/main.py**: FastAPI application with all routes and endpoints
- **app/models.py**: Database models (Recipe, Step, StepIngredient, IngredientConversion)
- **app/crud.py**: Database operations (create, read, update, delete)
- **app/schemas.py**: Pydantic models for request/response validation
- **app/scraper.py**: Recipe scraping from various cooking websites

## Import Structure

Since the code is organized in the `app/` package, imports should use:

```python
from app import models, crud, schemas, scraper
from app.database import engine, get_db
```

## Configuration

Configuration is handled through environment variables:
- `ADMIN_PASSWORD`: Password for editing recipes (default: "secret")
- `DB_PATH`: Database file location (default: "./rcpe.db")

See `.env.example` for a template.
