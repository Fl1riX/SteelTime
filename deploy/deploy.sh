#!/bin/bash

set -e

cd /home/fl1rix/SteelTime/

echo "----- Deploy started: $(date) -----" >> ./deploy.log

# Скачаиваем изменения
git fetch origin main >> ./deploy.log 2>&1

# Стираем любые незакоммиченные изменения
git checkout . >> ./deploy.log 2>&1

# Жестко приравниваем локальную ветку к удаленной
git checkout . >> ./deploy.log 2>&1

# Удаляем все неотслеживаемые файлы
git clean -fd >> ./deploy.log 2>&1

git status >> ./deploy.log 2>&1

# Обновляем и перезапускаем Docker
docker compose pull >> ./deploy.log 2>&1
docker compose up -d >> ./deploy.log 2>&1

echo "--- Deploy finished successfully ---" >> ./deploy.log