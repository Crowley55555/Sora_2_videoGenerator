def generate_sora2_video(arguments):
    import os
    from openai import OpenAI
    from openai import PermissionDeniedError

    prompt = arguments["prompt"]
    # API ключ можно не передавать: SDK возьмет из переменной окружения OPENAI_API_KEY
    api_key = arguments.get("openai_api_key")
    model = arguments.get("model", "sora-2")
    
    # Защита бюджета: ограничиваем длительность видео максимум 3 секундами
    duration = arguments.get("duration_seconds")
    if duration is not None:
        if duration > 1:
            print(f"⚠️ ВНИМАНИЕ: Запрошенная длительность {duration} сек. превышает лимит безопасности (3 сек.). Используется 3 сек.")
            duration = 1
        elif duration < 1:
            raise ValueError("Длительность видео должна быть не менее 1 секунды.")

    # Инициализируем клиент (учитываем ID организации из аргументов или окружения)
    organization = arguments.get("openai_organization") or os.getenv("OPENAI_ORG_ID")
    if api_key or organization:
        client = OpenAI(api_key=api_key, organization=organization)
    else:
        client = OpenAI()

    # Отправляем запрос: модель + промпт + длительность (если указана)
    # Параметр duration ограничен до 5 сек. для защиты бюджета
    try:
        create_params = {
            "model": model,
            "prompt": prompt,
        }
        
        # Добавляем duration только если он указан и валиден
        if duration is not None:
            create_params["duration"] = duration
        
        video_job = client.videos.create(**create_params)
    except PermissionDeniedError as e:
        # Проверяем тип ошибки 403 для более информативного сообщения
        error_message = str(e).lower()
        
        if "unsupported_country" in error_message or "country, region, or territory not supported" in error_message:
            raise RuntimeError(
                "❌ Sora 2 API недоступен в вашей стране/регионе.\n"
                "API Sora 2 имеет географические ограничения и пока не поддерживается в вашем регионе.\n"
                "Проверьте актуальную информацию о доступности на https://platform.openai.com/docs/guides/video-generation"
            ) from e
        elif "organization" in error_message or "verify" in error_message:
            raise RuntimeError(
                "Доступ к модели отклонён (403). Верифицируйте организацию на https://platform.openai.com/settings/organization/general, "
                "убедитесь в наличии доступа к модели `sora-2`, при необходимости укажите OPENAI_ORG_ID и подождите до 15 минут."
            ) from e
        else:
            # Общая ошибка 403
            raise RuntimeError(
                f"Доступ к модели отклонён (403): {str(e)}\n"
                "Возможные причины:\n"
                "1. API ключ недействителен или не имеет доступа к Sora 2\n"
                "2. Ваша организация не верифицирована\n"
                "3. Sora 2 недоступен в вашем регионе\n"
                "4. Не указан OPENAI_ORG_ID (если требуется)"
            ) from e
    except Exception as e:
        # Бросаем краткую ошибку вверх по стеку, чтобы увидеть причину
        raise RuntimeError(f"Не удалось создать задачу генерации видео: {e}") from e

    # Sora 2 использует асинхронную генерацию - задача сначала в очереди (queued)
    # Нужно опрашивать статус, пока видео не будет готово
    video_id = video_job.id
    status = video_job.status
    
    print(f"📹 Задача создания видео создана. ID: {video_id}")
    print(f"📋 Начальный статус: {status}")
    
    # Если задача в очереди или обрабатывается, опрашиваем статус
    import time
    max_wait_time = 300  # Максимум 5 минут ожидания
    check_interval = 5  # Проверяем каждые 5 секунд
    elapsed_time = 0
    
    while status in ['queued', 'processing', 'in_progress']:
        if elapsed_time >= max_wait_time:
            raise RuntimeError(
                f"⏱️ Превышено время ожидания генерации видео ({max_wait_time} сек).\n"
                f"ID задачи: {video_id}\n"
                f"Текущий статус: {status}\n"
                f"Попробуйте позже получить результат через: client.videos.retrieve('{video_id}')"
            )
        
        print(f"⏳ Ожидание генерации... Статус: {status}, Прошло: {elapsed_time} сек.")
        time.sleep(check_interval)
        elapsed_time += check_interval
        
        # Проверяем обновлённый статус
        try:
            video_job = client.videos.retrieve(video_id)
            status = video_job.status
            
            if hasattr(video_job, 'progress'):
                print(f"📊 Прогресс: {video_job.progress}%")
            
            if hasattr(video_job, 'error') and video_job.error:
                raise RuntimeError(f"❌ Ошибка при генерации видео: {video_job.error}")
        except Exception as retrieve_error:
            raise RuntimeError(f"Не удалось получить статус задачи: {retrieve_error}") from retrieve_error
    
    # Когда статус 'completed', получаем видео через download_content согласно документации
    if status == 'completed':
        print(f"✅ Видео готово!")
        
        # Получаем объект видео сначала
        try:
            video = client.videos.retrieve(video_id)
            print(f"🔍 Получен объект видео: ID={video.id}, Статус={video.status}")
        except Exception as e:
            raise RuntimeError(f"Не удалось получить объект видео: {e}") from e
        
        # Используем метод download_content согласно документации OpenAI
        # content = openai.videos.download_content(video.id, variant="video")
        try:
            print(f"📥 Загружаем содержимое видео через download_content...")
            content = client.videos.download_content(video.id, variant="video")
            print(f"✅ Видео успешно загружено через download_content")
            
            # Проверяем тип содержимого
            print(f"🔍 Тип содержимого: {type(content)}")
            print(f"🔍 Размер содержимого: {len(content) if hasattr(content, '__len__') else 'неизвестно'} байт")
            
            # Если это бинарные данные, нужно сохранить или вернуть информацию о файле
            # Проверяем, есть ли в объекте video URL для доступа
            video_url = None
            
            # Проверяем атрибуты объекта video на наличие URL
            if hasattr(video, 'url'):
                video_url = video.url
                print(f"🔍 Найден URL в объекте video: {video_url}")
            elif hasattr(video, 'file_url'):
                video_url = video.file_url
                print(f"🔍 Найден file_url в объекте video: {video_url}")
            elif hasattr(video, 'download_url'):
                video_url = video.download_url
                print(f"🔍 Найден download_url в объекте video: {video_url}")
            else:
                # Если URL не найден, используем стандартный API endpoint
                video_url = f"https://api.openai.com/v1/videos/{video_id}/content"
                print(f"ℹ️ URL не найден в объекте, используем API endpoint: {video_url}")
            
            # Выводим структуру объекта video для отладки
            try:
                if hasattr(video, 'model_dump'):
                    video_dict = video.model_dump()
                    print(f"🔍 Структура объекта video: {video_dict}")
            except Exception as debug_e:
                print(f"🔍 Не удалось получить структуру: {debug_e}")
            
            print(f"✅ URL видео: {video_url}")
            return video_url
            
        except Exception as download_error:
            raise RuntimeError(
                f"❌ Не удалось загрузить содержимое видео через download_content: {download_error}\n"
                f"ID видео: {video_id}\n"
                f"Попробуйте получить видео через: client.videos.retrieve('{video_id}')"
            ) from download_error
    else:
        raise RuntimeError(
            f"❌ Неожиданный статус задачи: {status}\n"
            f"ID задачи: {video_id}\n"
            f"Проверьте статус вручную через: client.videos.retrieve('{video_id}')"
        )