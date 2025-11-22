Online recipes are pretty awful - use this tool to store recipes in a clean and efficient manner with no ads/clutter.

# Deployment via Docker
```
mkdir mini-rcpe
cd mini-rcpe
nano docker-compose.yml # edit key values (e.g., database location, user credentials, port)
docker compose up -d
```

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
