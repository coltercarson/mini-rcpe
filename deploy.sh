#!/bin/bash

# Mini-RCPE Deployment Script for Linux
# This script helps you deploy Mini-RCPE using Docker

set -e

echo "==================================="
echo "Mini-RCPE Docker Deployment Script"
echo "==================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/engine/install/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Configuration
echo "Let's configure your Mini-RCPE instance:"
echo ""

# Admin Password
if [ -f .env ] && grep -q "ADMIN_PASSWORD" .env; then
    EXISTING_PASSWORD=$(grep ADMIN_PASSWORD .env | cut -d '=' -f2)
    echo "Existing admin password found: $EXISTING_PASSWORD"
    read -p "Keep this password? (y/n) [y]: " KEEP_PASSWORD
    KEEP_PASSWORD=${KEEP_PASSWORD:-y}
    
    if [[ $KEEP_PASSWORD =~ ^[Yy]$ ]]; then
        ADMIN_PASSWORD=$EXISTING_PASSWORD
    else
        read -sp "Enter new admin password: " ADMIN_PASSWORD
        echo ""
    fi
else
    read -sp "Enter admin password (leave empty for random): " ADMIN_PASSWORD
    echo ""
    
    if [ -z "$ADMIN_PASSWORD" ]; then
        ADMIN_PASSWORD=$(openssl rand -base64 12 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)
        echo "Generated random password: $ADMIN_PASSWORD"
    fi
fi

# Port Configuration
if [ -f .env ] && grep -q "APP_PORT" .env; then
    EXISTING_PORT=$(grep APP_PORT .env | cut -d '=' -f2)
    read -p "Port to expose [$EXISTING_PORT]: " APP_PORT
    APP_PORT=${APP_PORT:-$EXISTING_PORT}
else
    read -p "Port to expose [8000]: " APP_PORT
    APP_PORT=${APP_PORT:-8000}
fi

# Database Location
if [ -f .env ] && grep -q "DB_PATH" .env; then
    EXISTING_DB=$(grep DB_PATH .env | cut -d '=' -f2)
    read -p "Database path [$EXISTING_DB]: " DB_PATH
    DB_PATH=${DB_PATH:-$EXISTING_DB}
else
    read -p "Database path [/app/data/rcpe.db]: " DB_PATH
    DB_PATH=${DB_PATH:-/app/data/rcpe.db}
fi

echo ""
echo "Configuration Summary:"
echo "  Admin Password: ${ADMIN_PASSWORD:0:3}***"
echo "  Port: $APP_PORT"
echo "  Database: $DB_PATH"
echo ""
read -p "Proceed with this configuration? (y/n) [y]: " CONFIRM
CONFIRM=${CONFIRM:-y}

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Create/update .env file
echo "Updating configuration..."
cat > .env << EOF
# Mini-RCPE Configuration
ADMIN_PASSWORD=$ADMIN_PASSWORD
APP_PORT=$APP_PORT
DB_PATH=$DB_PATH
EOF

echo "✓ Configuration saved to .env"
echo ""

# Create necessary directories
echo "Creating data directories..."
mkdir -p data
mkdir -p static/uploads
echo "✓ Directories created"
echo ""

# Build and start the application
echo "Building and starting Docker containers..."
echo "This may take a few minutes on first run..."
echo ""

if command -v docker-compose &> /dev/null; then
    docker-compose up -d --build
else
    docker compose up -d --build
fi

echo ""
echo "==================================="
echo "✓ Deployment Complete!"
echo "==================================="
echo ""
echo "Your Mini-RCPE instance is now running!"
echo ""
echo "Access it at: http://localhost:$APP_PORT"
if command -v hostname &> /dev/null; then
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
    if [ -n "$LOCAL_IP" ]; then
        echo "Or from another device: http://$LOCAL_IP:$APP_PORT"
    fi
fi
echo ""
echo "Admin Password: $ADMIN_PASSWORD"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Restart:      docker-compose restart"
echo "  Update:       git pull && docker-compose up -d --build"
echo ""
echo "For more information, see README-DOCKER.md"
