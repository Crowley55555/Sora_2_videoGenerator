
from dotenv import load_dotenv

load_dotenv()
#
from sora_2 import generate_sora2_video
# from langfuse_config import langfuse, get_langfuse_handler
#
# # Инициализация Langfuse (модуль доступен и готов к использованию)
# # langfuse - объект для работы с Langfuse API
# # get_langfuse_handler() - функция для создания CallbackHandler (для LangChain)
#
# # Пример использования: можно создать handler для мониторинга
# langfuse_handler = get_langfuse_handler()
#
# result = generate_sora2_video({
#     "prompt": "Киберпанк-город ночью, дождь отражается в неоновых вывесках, летающие автомобили",
#     "model": "sora-2",
#     # duration/audio временно убраны, чтобы избежать 400 при неподдерживаемых полях
# })
# print(result)  # https://cdn.openai.com/sora2/xyz123.mp4

import os
from openai import OpenAI

# Инициализация клиента — замените на ваш ключ и организацию при необходимости
api_key = os.getenv("OPENAI_API_KEY")  # или передайте напрямую
organization = os.getenv("OPENAI_ORG_ID")  # опционально

client = OpenAI(api_key=api_key, organization=organization)

# Пример вызова генерации видео
try:
    video_obj = client.videos.create(
        model="sora-2",
        prompt="Киберпанк-город ночью, дождь, неоновые вывески"
    )

    print("Ответ от API:", video_obj)
    print("Есть ли url?", hasattr(video_obj, 'url'))
    print("Есть ли data?", hasattr(video_obj, 'data'))

    # Дополнительно: выведем все атрибуты объекта для отладки
    print("Все атрибуты:", [attr for attr in dir(video_obj) if not attr.startswith('_')])

except Exception as e:
    print("Ошибка при вызове API:", e)