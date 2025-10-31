def generate_sora2_video(arguments):
    import os
    import sys
    import time
    from openai import OpenAI
    
    prompt = arguments['prompt']
    model = "sora-2"
    openai_api_key = None
    openai_organization = None
    
    if 'model' in arguments:
        model = arguments['model']
    
    if 'openai_api_key' in arguments:
        openai_api_key = arguments['openai_api_key']
    else:
        openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if 'openai_organization' in arguments:
        openai_organization = arguments['openai_organization']
    else:
        openai_organization = os.getenv('OPENAI_ORG_ID')
    
    if not openai_api_key:
        raise ValueError("API ключ OpenAI не указан. Укажите openai_api_key в аргументах или установите переменную окружения OPENAI_API_KEY")
    
    if openai_organization:
        openai = OpenAI(api_key=openai_api_key, organization=openai_organization)
    else:
        openai = OpenAI(api_key=openai_api_key)
    
    video = openai.videos.create(
        model=model,
        prompt=prompt,
    )
    
    print("Video generation started:", video)
    
    progress = getattr(video, "progress", 0)
    bar_length = 30
    
    while video.status in ("in_progress", "queued"):
        # Refresh status
        video = openai.videos.retrieve(video.id)
        progress = getattr(video, "progress", 0)
        filled_length = int((progress / 100) * bar_length)
        bar = "=" * filled_length + "-" * (bar_length - filled_length)
        status_text = "Queued" if video.status == "queued" else "Processing"
        sys.stdout.write(f"\r{status_text}: [{bar}] {progress:.1f}%")
        sys.stdout.flush()
        time.sleep(2)
    
    # Move to next line after progress loop
    sys.stdout.write("\n")
    
    if video.status == "failed":
        message = getattr(
            getattr(video, "error", None), "message", "Video generation failed"
        )
        print(message)
        raise RuntimeError(f"Video generation failed: {message}")
    
    print("Video generation completed:", video)
    print("Downloading video content...")
    
    content = openai.videos.download_content(video.id, variant="video")
    
    # Получаем байты видео
    # content может быть разных типов в зависимости от версии SDK OpenAI
    import tempfile
    
    video_bytes = None
    
    # Пробуем разные способы получения байтов
    try:
        if isinstance(content, bytes):
            video_bytes = content
        elif hasattr(content, 'read'):
            # Если это файлоподобный объект с методом read
            if hasattr(content, 'seek'):
                content.seek(0)
            video_bytes = content.read()
        elif hasattr(content, 'content'):
            # Если это response объект
            video_bytes = content.content
        else:
            # Если content имеет метод write_to_file, сохраняем во временный файл и читаем байты
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            try:
                content.write_to_file(temp_file.name)
                with open(temp_file.name, 'rb') as f:
                    video_bytes = f.read()
            finally:
                os.unlink(temp_file.name)
    except Exception as e:
        raise RuntimeError(f"Не удалось получить байты видео: {str(e)}")
    
    if video_bytes is None or len(video_bytes) == 0:
        raise RuntimeError("Не удалось получить байты видео или файл пустой")
    
    print(f"Video size: {len(video_bytes) / 1024 / 1024:.2f} MB")
    
    print("Uploading video to temp.sh...")
    
    # Загружаем на temp.sh согласно документации
    import requests
    
    video_filename = f"sora_video_{video.id}.mp4"
    
    try:
        # Согласно документации temp.sh:
        # POST запрос на https://temp.sh/upload
        # files={"file": (filename, bytes, content_type)}
        # Ответ: просто URL в тексте (не JSON!)
        
        response = requests.post(
            "https://temp.sh/upload",
            files={"file": (video_filename, video_bytes, "video/mp4")},
            timeout=60
        )
        
        if response.status_code == 200:
            # temp.sh возвращает URL напрямую в тексте ответа
            download_url = response.text.strip()
            
            # Проверяем, что это действительно URL
            if download_url.startswith('http'):
                print(f"✅ Video uploaded successfully to temp.sh!")
                print(f"📥 Download link: {download_url}")
                print("ℹ️  File will be automatically deleted after download")
                return download_url
            else:
                raise RuntimeError(
                    f"temp.sh returned unexpected response format. "
                    f"Expected URL, got: {download_url[:200]}"
                )
        else:
            raise RuntimeError(
                f"Failed to upload file to temp.sh: HTTP {response.status_code} - {response.text[:500]}"
            )
    
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error while uploading to temp.sh: {str(e)}")
    
    except Exception as e:
        raise RuntimeError(f"Failed to upload file to temp.sh: {str(e)}")
