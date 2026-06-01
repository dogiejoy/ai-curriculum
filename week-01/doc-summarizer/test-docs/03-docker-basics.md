# Docker Compose Essentials

Docker Compose defines multi-container applications using a YAML file.
One `docker-compose.yml` configures all services, networks, and volumes.

## Service definition

Each service runs from an image. Specify with `image:` for prebuilt images
or `build:` to build from a Dockerfile. Common settings include `ports` for
port mapping, `environment` for env vars, and `volumes` for persistent storage.

## Volumes vs bind mounts

Named volumes (managed by Docker) survive container restarts. Bind mounts
(host path mapped to container path) are great for development since changes
on the host reflect immediately in the container.

## Networking

Compose creates a default network where services can reach each other by
service name as hostname. A `postgres` service is reachable from the `app`
service as `postgres:5432`.

## Lifecycle commands

`docker compose up -d` starts services in background. `down` stops and removes
containers. `down -v` also removes named volumes (dangerous — destroys data).
`logs -f` tails logs. `exec` runs a command in a running container.

## Healthchecks

Define healthchecks to ensure dependent services wait for the database to be
ready before starting. Use `depends_on` with `condition: service_healthy`.
