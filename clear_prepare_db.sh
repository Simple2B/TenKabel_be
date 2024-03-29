#!/bin/bash
echo Clearing up database
docker compose down -v &&
echo Starting db
docker compose up -d db &&
sleep 3
echo Applying migrations
alembic upgrade head &&
echo Creating data
#inv create-verified-user
echo init db
inv init-db --test-data
echo creating superuser
inv create-superuser
