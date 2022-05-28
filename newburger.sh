#!/bin/bash
set -e

cd /opt/star-burger
docker build -t star-burger-frontend -f Dockerfile.frontend .
docker run --rm -v $(pwd)/bundles:/opt/frontend/bundles star-burger-frontend


docker compose -f docker-compose.prod.yml down
git fetch
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

echo star-burged was updated and it will work soon!
