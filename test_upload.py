"""
Скрипт для тестирования загрузки файлов на temp.sh
без генерации видео через API (экономия токенов)
"""
import requests
import os
import tempfile


def test_file_upload(test_file_path=None):
    """
    Тестирует загрузку файла на temp.sh
    
    Args:
        test_file_path: Путь к тестовому файлу. Если None, создается временный файл
    """
    
    # Создаем или используем тестовый файл
    if test_file_path and os.path.exists(test_file_path):
        print(f"📁 Используем существующий файл: {test_file_path}")
        with open(test_file_path, 'rb') as f:
            file_bytes = f.read()
        filename = os.path.basename(test_file_path)
    else:
        # Создаем тестовый файл с небольшими данными
        print("📝 Создаем тестовый файл...")
        test_content = b"This is a test file for upload to temp.sh\n" * 100
        file_bytes = test_content
        filename = "test_upload.txt"
        print(f"✅ Создан тестовый файл размером {len(file_bytes)} байт")
    
    print(f"📊 Размер файла: {len(file_bytes) / 1024:.2f} KB")
    print("\n" + "="*60)
    print("Начинаем тестирование загрузки на temp.sh...")
    print("="*60 + "\n")
    
    download_url = None
    
    # Используем temp.sh согласно документации
    print("🔹 Загрузка на temp.sh (согласно документации)...")
    try:
        # Согласно документации temp.sh:
        # POST на https://temp.sh/upload
        # files={"file": (filename, bytes, content_type)}
        # Ответ: просто URL в тексте (не JSON!)
        
        response = requests.post(
            "https://temp.sh/upload",
            files={"file": (filename, file_bytes, "application/octet-stream")},
            timeout=30
        )
        
        print(f"   Status code: {response.status_code}")
        content_type = response.headers.get('Content-Type', '').lower()
        print(f"   Content-Type: {content_type}")
        
        if response.status_code == 200:
            # temp.sh возвращает URL напрямую в тексте
            download_url = response.text.strip()
            print(f"   Response text: {download_url[:200]}")
            
            # Проверяем, что это действительно URL
            if download_url.startswith('http'):
                print(f"   ✅ Успешно! URL: {download_url}")
                print(f"   ℹ️  Файл будет автоматически удален после скачивания")
            else:
                print(f"   ❌ Неверный формат ответа: ожидался URL, получено: {download_url[:200]}")
                return None
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
            print(f"   Ответ: {response.text[:500]}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка сети: {str(e)}")
    except Exception as e:
        print(f"   ❌ Исключение: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()[:200]}")
    
    # Результаты
    print("\n" + "="*60)
    if download_url:
        print("✅ РЕЗУЛЬТАТ: Файл успешно загружен!")
        print(f"📦 Использован сервис: temp.sh")
        print(f"🔗 URL для скачивания: {download_url}")
        print("ℹ️  Файл будет автоматически удален после скачивания")
        
        # Пробуем проверить доступность файла
        print("\n🔍 Проверяем доступность файла...")
        try:
            check_response = requests.head(download_url, timeout=10, allow_redirects=True)
            print(f"   Status code: {check_response.status_code}")
            if check_response.status_code in [200, 302]:
                print("   ✅ Файл доступен для скачивания!")
            else:
                print(f"   ⚠️  Файл может быть недоступен (код: {check_response.status_code})")
        except Exception as e:
            print(f"   ⚠️  Не удалось проверить доступность: {str(e)[:50]}")
        
        return download_url
    else:
        print("❌ РЕЗУЛЬТАТ: Не удалось загрузить файл на temp.sh")
        print("💡 Возможные причины:")
        print("   - Проблемы с интернет-соединением")
        print("   - Временная недоступность сервиса")
        print("   - Файл слишком большой")
        return None


if __name__ == "__main__":
    print("="*60)
    print("🧪 Тестирование загрузки файлов на temp.sh")
    print("="*60 + "\n")
    
    # Можно указать свой файл для тестирования
    # test_file = "path/to/your/test/file.mp4"
    # result = test_file_upload(test_file)
    
    # Или просто протестировать с автоматически созданным файлом
    result = test_file_upload()
    
    if result:
        print(f"\n✅ Тест завершен успешно!")
        print(f"💡 Скопируйте эту ссылку и проверьте в браузере: {result}")
    else:
        print(f"\n❌ Тест завершен с ошибками")
        print("💡 Проверьте интернет-соединение и попробуйте еще раз")

