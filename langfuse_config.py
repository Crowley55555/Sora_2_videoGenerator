# Модуль подключения к Langfuse для мониторинга
import os
from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

# Загрузка переменных окружения
load_dotenv()

# Переменные окружения для Langfuse
langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

# Инициализация Langfuse
langfuse = Langfuse(
    public_key=langfuse_public_key,
    secret_key=langfuse_secret_key,
    host=langfuse_host
)

# Функция для создания CallbackHandler для мониторинга через Langfuse
def get_langfuse_handler():
    """
    Создает и возвращает CallbackHandler для мониторинга через Langfuse
    
    Returns:
        CallbackHandler: Обработчик для использования в LangChain
    """
    return CallbackHandler()

