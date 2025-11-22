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
│   ├── test_scrape.py     # Scraper tests
│   ├── test_multi_recipe.py
│   └── test_ingredient_distribution.py
│
├── README.md              # Main documentation
├── README-DOCKER.md       # Docker deployment guide
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container build configuration
├── docker-compose.yml     # Multi-container deployment
├── deploy.sh              # Deployment helper script
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
├── .dockerignore          # Docker ignore rules
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
