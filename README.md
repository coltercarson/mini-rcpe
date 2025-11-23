Online recipes are pretty awful - use this tool to store recipes in a clean and efficient manner with no ads/clutter.

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
