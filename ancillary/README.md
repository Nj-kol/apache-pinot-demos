## Ancillary Components for Demo

1. S3
2. Redis

## Usage

```bash
## Start all components
docker-compose -f ancillary-components.yml up -d

## Stop all components
docker-compose -f ancillary-components.yml down
```

## UI

**Minio S3**
- URL : http://localhost:9001/browser/
- user/pass : minio/minio123

**Redis**
- URL : http://localhost:8001/redis-stack/browser
