#!/bin/bash
source ../.venv/bin/activate
celery -A project beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
