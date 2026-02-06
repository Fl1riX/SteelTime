# This Python code snippet is setting up a logging configuration for a service booking system API.
import logging

logger = logging.getLogger("Service-Booking-System_api")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') # задаем формат логов

console_handler = logging.StreamHandler() # вывод логов в консоль
console_handler.setFormatter(formatter)

handler = logging.FileHandler(filename="SteelTime.log", encoding="utf-8") # файл для записи логов
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(console_handler)