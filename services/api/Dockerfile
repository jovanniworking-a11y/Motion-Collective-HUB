# MOTION Control Plane API — cloud image (Fly / Railway / Render)
# Build context MUST be the monorepo root (not services/api alone):
#   docker build -f services/api/Dockerfile -t motion-api .
#
# Free-tier note: SQLite under MOTION_DATA_DIR resets on redeploy unless a volume is attached.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MOTION_DATA_DIR=/tmp/motion-api-data \
    MOTION_REPO_ROOT=/srv \
    PORT=8787

WORKDIR /srv

# Keep repo-relative paths (config.py parents[3] = /srv when MOTION_REPO_ROOT unset)
COPY services/api/requirements.txt /srv/services/api/requirements.txt
RUN pip install --no-cache-dir -r /srv/services/api/requirements.txt

COPY services/api/app /srv/services/api/app
# Activity feed + Muse embed (safe; no guest PII in orch trees we ship)
COPY orch /srv/orch

WORKDIR /srv/services/api

EXPOSE 8787

# Railway/Fly inject PORT; default 8787 for local docker run
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8787}"]
