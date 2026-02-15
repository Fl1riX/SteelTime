import time

from src.logger import logger
from fastapi  import Request
from starlette.responses import Response
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request, # запрос от клиента
        call_next: Callable # следующий middleware или endpoint
    ) -> Response:
        """Кастомный middleware. Логирует все запросы + метрики производительности"""
        startup_time = time.perf_counter() # запускаем секундомер
        client_ip = (
            request.client.host if request.client and request.client.host 
            else "unknown" 
        ) # получаем ip клиента
        user_agent = request.headers.get("user-agent", "unknown")[:100] # получаем браузер или приложение

        logger.info(
            f"REQUEST | {client_ip} | {request.method} {request.url.path} | "
            f"UA: '{user_agent}'"
        )    

        # вызываем endpoint
        response: Response = await call_next(request) # передаем запрос дальше и ожидаем ответ

        # логируем исходящий ответ
        process_time = time.perf_counter() - startup_time # вычисляем сколько заняла обработка запроса
        response_size = len(response.body) if hasattr(response, "body") and response.body else 0 # размер тела ответа

        logger.info(
            f"RESPONSE | {request.method} {request.url.path} | "
            f"{response.status_code} | {process_time:.3f}s | {response_size}b"
        )

        # добавляем заголовки
        # нужно для сборщиков метрики как Прометеус\Grafana
        response.headers["X-Process-Time"] = f"{process_time}"
        response.headers["X-Response-Size"] = str(response_size)

        return response