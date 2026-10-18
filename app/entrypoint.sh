#!/bin/sh
# Container start: apply migrations, seed the test user, then serve the app.
set -e

alembic -c app/alembic.ini upgrade head
python -m app.seed

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
