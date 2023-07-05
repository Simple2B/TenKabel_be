#!/bin/bash
echo Starting worker
poetry run celery -A app.controller.celery worker -B --loglevel=INFO
