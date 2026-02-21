#!/bin/bash
set -e # Упадет при любой ошибке
alembic upgrade head 
uvicorn main:app --host 0.0.0.0 --port 8000