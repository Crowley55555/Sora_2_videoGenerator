import os
from dotenv import load_dotenv

load_dotenv()

from sora_2 import generate_sora2_video



result = generate_sora2_video({
    "prompt": "Киберпанк-город ночью, дождь отражается в неоновых вывесках, летающие автомобили",
    "model": "sora-2",
    # duration/audio временно убраны, чтобы избежать 400 при неподдерживаемых полях
})
print(result)  # https://cdn.openai.com/sora2/xyz123.mp4