# Docker Deployment Guide for pyResToolbox MCP Server

This guide explains how to deploy the pyResToolbox MCP server using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

### Option 1: HTTP Server (Recommended for Web Access)

```bash
# Start HTTP server on port 8000
docker-compose --profile http up -d

# Check logs
docker-compose logs -f pyrestoolbox-mcp-http

# Stop server
docker-compose --profile http down
```

Access the server at: `http://localhost:8000`

### Option 2: SSE Server (Server-Sent Events)

```bash
# Start SSE server on port 8001
docker-compose --profile sse up -d

# Check logs
docker-compose logs -f pyrestoolbox-mcp-sse

# Stop server
docker-compose --profile sse down
```

Access the server at: `http://localhost:8001`

### Option 3: STDIO Server (for Programmatic Access)

```bash
# Start STDIO server
docker-compose --profile stdio up -d

# Interact with server
docker exec -it pyrestoolbox-mcp-stdio fastmcp run server.py

# Stop server
docker-compose --profile stdio down
```

## Building the Docker Image

### Build with Docker

```bash
# Build the image
docker build -t pyrestoolbox-mcp:latest .

# Run with STDIO
docker run -it pyrestoolbox-mcp:latest

# Run with HTTP
docker run -p 8000:8000 pyrestoolbox-mcp:latest \
  fastmcp run server.py --transport http --host 0.0.0.0 --port 8000
```

### Build with Docker Compose

```bash
# Build all services
docker-compose build

# Build specific profile
docker-compose --profile http build
```

## Environment Configuration

Copy `.env.docker` to `.env` and customize:

```bash
cp .env.docker .env
```

Available environment variables:

```env
# HTTP Server Port
MCP_HTTP_PORT=8000

# SSE Server Port
MCP_SSE_PORT=8001

# Logging Level
LOG_LEVEL=INFO
```

## Docker Compose Profiles

The `docker-compose.yml` uses profiles to run different transport modes:

| Profile | Service Name | Port | Use Case |
|---------|-------------|------|----------|
| `http` | pyrestoolbox-mcp-http | 8000 | Web/HTTP access |
| `sse` | pyrestoolbox-mcp-sse | 8001 | Server-Sent Events |
| `stdio` | pyrestoolbox-mcp-stdio | N/A | Programmatic/CLI access |

## Common Operations

### Start Server

```bash
# HTTP server
docker-compose --profile http up -d

# Multiple profiles
docker-compose --profile http --profile sse up -d
```

### View Logs

```bash
# Follow logs
docker-compose logs -f

# Specific service
docker-compose logs -f pyrestoolbox-mcp-http

# Last 100 lines
docker-compose logs --tail=100 pyrestoolbox-mcp-http
```

### Stop Server

```bash
# Stop specific profile
docker-compose --profile http down

# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Restart Server

```bash
# Restart specific service
docker-compose restart pyrestoolbox-mcp-http

# Restart all
docker-compose restart
```

### Execute Commands

```bash
# Run test inside container
docker exec pyrestoolbox-mcp-http python test_server.py

# Access shell
docker exec -it pyrestoolbox-mcp-http /bin/bash

# Check server status
docker exec pyrestoolbox-mcp-http python -c "from pyrestoolbox_mcp import mcp; print(mcp.name)"
```

## Health Checks

The HTTP and SSE services include health checks:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' pyrestoolbox-mcp-http

# View health check logs
docker inspect --format='{{json .State.Health}}' pyrestoolbox-mcp-http | jq
```

## Integration Examples

### With Claude Desktop (HTTP Transport)

1. Start HTTP server:
```bash
docker-compose --profile http up -d
```

2. Update Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "pyrestoolbox": {
      "url": "http://localhost:8000"
    }
  }
}
```

### With Python Client (HTTP)

```python
import httpx

# Call a tool via HTTP
response = httpx.post(
    "http://localhost:8000/tools/oil_bubble_point",
    json={
        "api": 35.0,
        "degf": 180.0,
        "rsb": 800.0,
        "sg_g": 0.75,
        "method": "VALMC"
    }
)
print(response.json())
```

### With Docker Network

To connect from another container:

```yaml
services:
  your-app:
    image: your-app:latest
    networks:
      - pyrestoolbox-mcp-network
    environment:
      - MCP_SERVER_URL=http://pyrestoolbox-mcp-http:8000

networks:
  pyrestoolbox-mcp-network:
    external: true
```

## Production Deployment

### Security Considerations

1. **Use a reverse proxy** (nginx, traefik) for HTTPS:
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - pyrestoolbox-mcp-http
```

2. **Add authentication** using FastMCP auth providers

3. **Limit resource usage**:
```yaml
services:
  pyrestoolbox-mcp-http:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Scaling

Run multiple replicas:

```yaml
services:
  pyrestoolbox-mcp-http:
    deploy:
      replicas: 3
    # ... rest of config
```

Or use Docker Swarm/Kubernetes for orchestration.

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs pyrestoolbox-mcp-http

# Check if port is in use
lsof -i :8000

# Remove and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose --profile http up
```

### Import Errors

```bash
# Verify installation
docker exec pyrestoolbox-mcp-http pip list | grep pyrestoolbox

# Reinstall
docker-compose build --no-cache
```

### Permission Issues

The container runs as non-root user (uid 1000). If you have permission issues:

```bash
# Check user
docker exec pyrestoolbox-mcp-http whoami

# Fix ownership
docker exec -u root pyrestoolbox-mcp-http chown -R mcp:mcp /app
```

### Network Issues

```bash
# Check network
docker network ls | grep mcp

# Inspect network
docker network inspect pyrestoolbox-mcp-network

# Recreate network
docker network rm pyrestoolbox-mcp-network
docker-compose up -d
```

## Maintenance

### Update Image

```bash
# Pull latest code
git pull

# Rebuild image
docker-compose build

# Restart with new image
docker-compose --profile http down
docker-compose --profile http up -d
```

### Cleanup

```bash
# Remove unused images
docker image prune -a

# Remove all related containers and images
docker-compose down --rmi all

# Remove volumes
docker volume rm pyrestoolbox-mcp-data
```

## Advanced Configuration

### Custom Dockerfile

Create `Dockerfile.custom`:

```dockerfile
FROM pyrestoolbox-mcp:latest

# Add custom dependencies
RUN pip install your-custom-package

# Add custom configuration
COPY custom-config.py /app/
```

Build:
```bash
docker build -f Dockerfile.custom -t pyrestoolbox-mcp:custom .
```

### Development Mode

Mount source code for live development:

```yaml
services:
  pyrestoolbox-mcp-dev:
    build: .
    volumes:
      - ./src:/app/src:ro
    command: ["fastmcp", "run", "server.py", "--reload"]
```

## Monitoring

### Container Stats

```bash
# Real-time stats
docker stats pyrestoolbox-mcp-http

# Resource usage
docker-compose top
```

### Logs to File

```bash
# Export logs
docker-compose logs > mcp-server.log

# With timestamp
docker-compose logs --timestamps > mcp-server.log
```

## Support

For Docker-specific issues:
- Check logs: `docker-compose logs`
- Verify health: `docker-compose ps`
- Test connectivity: `curl http://localhost:8000`

For application issues, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).
