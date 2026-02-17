#!/usr/bin/bash

set -eux

# Include demo media data in build
cp -r tesys_tagboard/fixtures/uploads/ tesys_tagboard/media/
cp -r tesys_tagboard/fixtures/thumbnails/ tesys_tagboard/media/

docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d postgres
docker compose -f docker-compose.production.yml run --rm django python manage.py migrate
docker compose -f docker-compose.production.yml run --rm django python manage.py loaddata demo.json
docker compose -f docker-compose.production.yml up -d
