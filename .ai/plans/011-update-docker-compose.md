This is a well-known issue: you're using docker-compose v1 (the Python-based version), which is incompatible with newer Docker Engine versions. The
   KeyError: 'ContainerConfig' happens because newer Docker Engine API responses changed the container inspect format, and docker-compose v1 can't
  parse it.

  The traceback confirms this — File "docker-compose", line 3 and File "compose/cli/main.py" are the Python-based v1.

  The fix: switch to docker compose v2 (the Go-based plugin, no hyphen). It ships as a Docker CLI plugin (docker compose instead of docker-compose).

  Check what you have on the server:

  docker compose version

  If it's available, update the Makefile to use docker compose instead of docker-compose:

  Read 1 file (ctrl+o to expand)

● Now I'll replace all docker-compose calls with docker compose (v2). Note: the --compatibility flag is no longer needed in v2 since it natively
  supports the deploy section.
