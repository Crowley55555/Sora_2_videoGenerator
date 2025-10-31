import os
from dotenv import load_dotenv
from sora_2 import generate_sora2_video

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем переменные окружения
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_organization = os.getenv('OPENAI_ORG_ID')

result = generate_sora2_video({
    "prompt": "видео длиной длиной 1 секунду: Киберпанк-город ночью, дождь отражается в неоновых вывесках, летающие автомобили ",
    "model": "sora-2",  # Быстрая модель (или "sora-2-pro" для высокого качества)
    "openai_api_key": openai_api_key,
    "openai_organization": openai_organization
})
print(f"✅ Download link: {result}\n")


