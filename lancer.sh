#!/bin/bash
cd "$(dirname "$(readlink -f "$0")")"
source venv/bin/activate
( until curl -s "http://localhost:8000/reveal?id=0" >/dev/null; do sleep 2; done; xdg-open http://localhost:8000 ) &
exec uvicorn server:app --host 0.0.0.0 --port 8000
