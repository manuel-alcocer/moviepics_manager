#!/bin/bash
source ../.venv/bin/activate
celery -A project worker -l INFO -c 1 -E
