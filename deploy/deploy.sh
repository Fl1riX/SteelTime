#!/bin/bash

set -e
cd /home/fl1rix/SteelTime/

# Включаем автоматическое логирование ВСЕГО скрипта в файл
exec >> ./deploy.log 2>&1

echo "----- Deploy started: $(date) -----"

# Скачиваем изменения из репозитория
git fetch origin main

# Стираем любые изменения в текущих файлах
git checkout .

# Жестко двигаем ветку вперед до актуального состояния на GitHub/GitLab
git reset --hard origin/main

# Удаляем весь случайный мусор и новые неотслеживаемые файлы
git clean -fd

git status

# Обновляем и перезапускаем Docker
docker compose pull
docker compose up -d

echo "--- Deploy finished successfully ---"
