#!/bin/bash

set -e

cd /home/fl1rix/SteelTime/

echo "----- Deploy started: $(date) -----" >> ./deploy.log

git pull origin main >> ./deploy.log 2>&1
git status >> ./deploy.log 2>&1

docker compose pull >> ./deploy.log 2>&1
docker compose up -d >> ./deploy.log 2>&1

echo "--- Deploy finished successfully ---" >> ./deploy.log