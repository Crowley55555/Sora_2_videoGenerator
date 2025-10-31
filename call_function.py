import os
from dotenv import load_dotenv
from sora_2 import generate_sora2_video

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем переменные окружения
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_organization = os.getenv('OPENAI_ORG_ID')

# # Пример 1: Базовый вызов с минимальными параметрами
# print("=== Пример 1: Базовый вызов ===")
# result1 = generate_sora2_video({
#     "prompt": "A video of a cool cat on a motorcycle in the night",
#     "openai_api_key": openai_api_key,
#     "openai_organization": openai_organization
# })
# print(f"Video saved to: {result1}\n")
#
# # Пример 2: Вызов с настройкой модели и длительности
# print("=== Пример 2: С настройкой модели и длительности ===")
# result2 = generate_sora2_video({
#     "prompt": "Киберпанк-город ночью, дождь отражается в неоновых вывесках",
#     "model": "sora-2-pro",  # Высокое качество
#     "duration_seconds": 5,  # Максимальная длительность
#     "openai_api_key": openai_api_key,
#     "openai_organization": openai_organization
# })
# print(f"Video saved to: {result2}\n")

# Пример 3: Вызов с настройкой модели (duration_seconds и has_audio пока не поддерживаются API)
print("=== Пример 3: С настройкой модели ===")
result3 = generate_sora2_video({
    "prompt": "Киберпанк-город ночью, дождь отражается в неоновых вывесках, летающие автомобили длиной 1 секунды",
    "model": "sora-2",  # Быстрая модель (или "sora-2-pro" для высокого качества)
    # "duration_seconds": 1,  # Пока не поддерживается API - будет проигнорировано
    # "has_audio": True,  # Пока не поддерживается API - будет проигнорировано
    "openai_api_key": openai_api_key,
    "openai_organization": openai_organization
})
print(f"Video saved to: {result3}\n")

# # Пример 4: Вызов только с длительностью (переменные окружения берутся автоматически)
# print("=== Пример 4: Только с длительностью (API ключ из окружения) ===")
# result4 = generate_sora2_video({
#     "prompt": "Aerial view of a futuristic city",
#     "duration_seconds": 2
#     # openai_api_key и openai_organization берутся из переменных окружения автоматически
# })
# print(f"Video saved to: {result4}\n")

