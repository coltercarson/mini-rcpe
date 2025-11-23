# Docker Configuration

This directory contains all Docker-related configuration files for Mini-RCPE.

## Files

- **Dockerfile** - Container build configuration
- **docker-compose.yml** - Multi-container deployment configuration
- **.dockerignore** - Files to exclude from Docker build context
- **deploy.sh** - Automated deployment script for Linux

## Quick Start

From the repository root:

```bash
# Start the application
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop the application
docker-compose -f docker/docker-compose.yml down
```

## Automated Deployment (Linux)

For an interactive deployment experience on Linux:

```bash
cd docker
./deploy.sh
```

The script will guide you through configuration and automatically start the application.

## Documentation

For complete Docker deployment instructions, see [../docs/README-DOCKER.md](../docs/README-DOCKER.md)
