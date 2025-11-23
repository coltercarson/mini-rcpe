# Mini-RCPE Docker Deployment Guide

Deploy Mini-RCPE using Docker on a Linux server in 3 simple steps.

## Prerequisites

- Docker and Docker Compose installed on your Linux server
- Basic familiarity with command line

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url> mini-rcpe
   cd mini-rcpe
   ```

2. **Edit docker/docker-compose.yml to configure:**
   ```bash
   nano docker/docker-compose.yml
   ```
   
   Change these settings:
   - `ADMIN_PASSWORD=changeme` - Set your admin password
   - `"8000:8000"` - Change first number to use different port (e.g., `"3000:8000"`)

3. **Start the application:**
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

4. **Access your recipes:**
   - Open `http://your-server-ip:8000` (or your configured port)
   - Login with your configured password

## Configuration

All configuration is done directly in `docker/docker-compose.yml`:

```yaml
environment:
  # Change your admin password here
  - ADMIN_PASSWORD=changeme
  # Database location (usually no need to change)
  - DB_PATH=/app/data/rcpe.db

ports:
  # Change the first number to use a different port
  - "8000:8000"
```

## Common Commands

```bash
# Start
docker-compose -f docker/docker-compose.yml up -d

# Stop
docker-compose -f docker/docker-compose.yml down

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Restart
docker-compose -f docker/docker-compose.yml restart

# Update to latest version
git pull && docker-compose -f docker/docker-compose.yml up -d --build
```

## Data Persistence

Your data is automatically saved in:
- **Database**: `./data/rcpe.db`
- **Images**: `./app/static/uploads/`

Data persists across container restarts and updates.

## Backup

To backup your data:

```bash
# Backup database
cp data/rcpe.db rcpe.db.backup

# Backup uploads
tar -czf uploads-backup.tar.gz app/static/uploads/
```

## Reverse Proxy Setup (Optional)

For production deployment with a domain name, use Nginx or Caddy as a reverse proxy.

### Nginx Example

```nginx
server {
    listen 80;
    server_name recipes.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Caddy Example (with automatic HTTPS)

Create a `Caddyfile`:

```
recipes.yourdomain.com {
    reverse_proxy localhost:8000
}
```

Run Caddy:
```bash
caddy run
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose -f docker/docker-compose.yml logs

# Check if port is already in use
sudo netstat -tulpn | grep 8000
```

### Permission issues with volumes
```bash
# Fix ownership
sudo chown -R 1000:1000 data app/static/uploads
```

### Database locked errors
```bash
# Restart the container
docker-compose -f docker/docker-compose.yml restart
```

## Security Recommendations

1. **Change the default password** in `docker/docker-compose.yml`
2. **Use a reverse proxy** with HTTPS in production
3. **Restrict port access** using firewall rules
4. **Regular backups** of the database and uploads
5. **Keep Docker images updated**: `docker-compose -f docker/docker-compose.yml pull && docker-compose -f docker/docker-compose.yml up -d`

## Updating

To update to a new version:

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker/docker-compose.yml up -d --build
```

Your data will be preserved during updates.

## Uninstalling

To completely remove the application:

```bash
# Stop and remove containers
docker-compose -f docker/docker-compose.yml down

# Remove data (WARNING: This deletes all recipes!)
rm -rf data app/static/uploads

# Remove Docker image
docker rmi mini-rcpe-web
```
