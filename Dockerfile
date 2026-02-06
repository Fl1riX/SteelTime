# Базовый легкий образ
FROM python:3.13-slim    

# Рабочая папка внтри контейнера
# создаем папку /app. Весь код будет тут
WORKDIR /app

# Копируем только requrements.txt(кэшируется)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Открываем порт
EXPOSE 8000

# Запуск
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


