#!/bin/bash

set -e

cd /home/fl1rix/SteelTime/

git pull origin main
docker compose pull
docker compose up -d