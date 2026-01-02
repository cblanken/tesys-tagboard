export COMPOSE_FILE := "docker-compose.local.yml"
export COMPOSE_PROFILES := "all"

## Just does not yet manage signals for subprocesses reliably, which can lead to unexpected behavior.
## Exercise caution before expanding its usage in production environments.
## For more information, see https://github.com/casey/just/issues/2473 .


# Default command to list all available commands
default:
    @just --list

# Build container images
build *args:
    @echo "Building container images..."
    @docker compose build {{args}}

# Start up containers
up *args:
    @echo "Starting up containers..."
    @docker compose up -d --remove-orphans {{args}}

# Start up containers and attach python debugger
up-debug:
    @echo "Starting up containers with debug console for Django app..."
    @docker compose --profile debug up -d --remove-orphans
    @docker compose run --rm --service-ports django # to handle python breakpoints
    # Note when exiting (Ctrl-C) the debugger, the other docker services
    # will remain up until brought down with `just down`

# Start up docs container
up-docs *args:
    @echo "Starting up docs container..."
    COMPOSE_FILE=docker-compose.docs.yml docker compose up -d {{args}}

# Stop containers
down *args:
    @echo "Stopping containers..."
    @docker compose down {{args}}

# Stop docker "debug" profile containers
down-debug:
    @echo "Stopping containers required for Django app debug..."
    @docker compose --profile debug down

# Stop docs container
down-docs:
    @echo "Stopping docs container..."
    COMPOSE_FILE=docker-compose.docs.yml docker compose down

# Remove containers and their volumes
prune-volumes *args:
    @echo "Killing containers and removing volumes..."
    @docker compose down -v {{args}}

# View container logs
logs *args:
    @docker compose logs -f {{args}}

alias t := test
# Run pytest(s)
test *args:
    @docker compose run --rm django pytest {{args}}

# Run pytest(s) with coverage report
coverage *args:
    @docker compose run --rm django coverage run -m pytest
    @docker compose run --rm django coverage report {{args}}

# Creates db backup in the /backups dir of postgres container
db-backup *args:
    @docker compose exec postgres backup

# Remove all postgres backups in /backups
db-rm-backups *args:
    @docker compose exec -t postgres sh -c 'rm -f /backups/*'

alias m := manage
# Django management CLI
manage *args:
    @docker compose exec -t django uv run python manage.py {{args}}

alias r := run
# Start the Django app on the host system
run:
    @echo "Starting Tesy's Tagboard..."
    DJANGO_READ_DOT_ENV_FILE=True uv run python manage.py tailwind dev

alias ra := run-async
# Start the Django app on the host system via uvicorn (asgi)
run-async *args:
    @echo "Starting Tesy's Tagboard in async mode..."
    DJANGO_READ_DOT_ENV_FILE=True uv run uvicorn config.asgi:application --host 0.0.0.0 --port 55555 --reload-include "*.html" {{ args }}

# Reset the database and prompt for a new admin password
db-reset:
    just manage reset_db
    just manage migrate
    just manage createsuperuser --username admin --email tesy-tagboard@example.com

alias mkc := make-component
# Create a new django-component with a given name
make-component name:
    #!/usr/bin/env bash
    set -euxo pipefail
    pascal=$(echo '{{name}}' | sed -r 's/(^|_)([a-z])/\U\2/g')
    class_name="${pascal}Component"
    echo "Making '{{name}}' component"
    dir="./tesys_tagboard/components/{{name}}"
    mkdir "$dir"
    py_file="$dir/{{name}}.py"
    touch "$py_file"
    touch "$dir/__init__.py"
    touch "$dir/{{name}}.html"
    touch "$dir/{{name}}.js"
    echo 'from django_components import Component' >> "$py_file"
    echo 'from django_components import register' >> "$py_file"
    echo '' >> "$py_file"
    echo '' >> "$py_file"
    echo '@register("{{name}}")' >> "$py_file"
    echo "class ${class_name}(Component):" >> "$py_file"
    echo '    template_file = "{{name}}.html"' >> "$py_file"
    echo '    js_file = "{{name}}.js"' >> "$py_file"

# Load the fixture data from demo.json into the database
load-demo:
    @echo "Loading demo data..."
    DJANGO_READ_DOT_ENV_FILE=True just manage loaddata demo.json
    cp -r tesys_tagboard/fixtures/uploads tesys_tagboard/media/
    cp -r tesys_tagboard/fixtures/thumbnails tesys_tagboard/media/

# Save the current database into the demo.json fixture
save-demo:
    @echo "Saving demo fixture..."
    just manage dumpdata --exclude admin --exclude sessions --indent 2 -o tesys_tagboard/fixtures/demo.json
