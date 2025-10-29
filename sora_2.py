def generate_sora2_video(arguments):
    import os
    from openai import OpenAI
    from openai import PermissionDeniedError

    prompt = arguments["prompt"]
    # API ключ можно не передавать: SDK возьмет из переменной окружения OPENAI_API_KEY
    api_key = arguments.get("openai_api_key")
    model = arguments.get("model", "sora-2")

    # Инициализируем клиент (учитываем ID организации из аргументов или окружения)
    organization = arguments.get("openai_organization") or os.getenv("OPENAI_ORG_ID")
    if api_key or organization:
        client = OpenAI(api_key=api_key, organization=organization)
    else:
        client = OpenAI()

    # Отправляем минимально необходимый запрос: модель + промпт
    # Доп. параметры (duration/audio) могут быть недоступны и вызывать 400
    try:
        video_job = client.videos.create(
            model=model,
            prompt=prompt,
        )
    except PermissionDeniedError as e:
        raise RuntimeError(
            "Доступ к модели отклонён (403). Верифицируйте организацию на https://platform.openai.com/settings/organization/general, "
            "убедитесь в наличии доступа к модели `sora-2`, при необходимости укажите OPENAI_ORG_ID и подождите до 15 минут."
        ) from e
    except Exception as e:
        # Бросаем краткую ошибку вверх по стеку, чтобы увидеть причину
        raise RuntimeError(f"Не удалось создать задачу генерации видео: {e}")

    return video_job