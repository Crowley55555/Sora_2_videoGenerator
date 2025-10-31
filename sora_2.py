def generate_sora2_video(arguments):
    import os
    import sys
    import time
    from openai import OpenAI
    
    prompt = arguments['prompt']
    model = "sora-2"
    duration_seconds = None
    has_audio = False
    openai_api_key = None
    openai_organization = None
    
    if 'model' in arguments:
        model = arguments['model']
    
    # Примечание: duration_seconds пока не поддерживается API, но оставляем для будущего
    if 'duration_seconds' in arguments:
        duration_seconds = arguments['duration_seconds']
        print("⚠️ ВНИМАНИЕ: Параметр duration_seconds пока не поддерживается Sora 2 API и будет проигнорирован")
    
    # Примечание: has_audio пока не поддерживается API, но оставляем для будущего
    if 'has_audio' in arguments:
        has_audio = arguments['has_audio']
        if has_audio:
            print("⚠️ ВНИМАНИЕ: Параметр has_audio пока не поддерживается Sora 2 API и будет проигнорирован")
    
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
    
    # Текущая версия Sora 2 API поддерживает только model и prompt
    # Параметры duration и audio пока не поддерживаются
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
    
    import tempfile
    temp_dir = tempfile.gettempdir()
    video_filename = f"video_{video.id}.mp4"
    video_path = os.path.join(temp_dir, video_filename)
    
    content.write_to_file(video_path)
    print(f"Wrote {video_path}")
    
    return video_path
