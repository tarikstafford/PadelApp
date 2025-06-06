#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# The entrypoint script is now only responsible for executing the command passed to it.
# The database migration command will be run as a separate "deploy" command in Railway.
echo "Executing main container command..."
exec "$@" 