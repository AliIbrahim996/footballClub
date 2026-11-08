#!/bin/sh
set -e
python manage.py migrate --noinput
if [ "$SEED_DEMO_DATA" = "1" ]; then
  # Only seed an empty database.
  python manage.py shell -c "import sys; from players.models import Player; sys.exit(1 if Player.objects.exists() else 0)" \
    && python manage.py seed --admin || true
fi
exec "$@"