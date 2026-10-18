#!/bin/sh
# Container start: apply migrations, then serve the app.
set -e

alembic -c app/alembic.ini upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
