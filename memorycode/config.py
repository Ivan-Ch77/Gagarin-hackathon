from dotenv import load_dotenv
import os

load_dotenv()

# Определение основных переменных конфигурации
MEMORYCODE_BASE_URL = os.getenv('MEMORYCODE_BASE_URL')
MEMORYCODE_EMAIL = os.getenv('MEMORYCODE_EMAIL')
MEMORYCODE_PASSWORD = os.getenv('MEMORYCODE_PASSWORD')
