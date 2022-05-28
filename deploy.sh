#!/bin/bash
set -e

cd /opt/star-burger
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
