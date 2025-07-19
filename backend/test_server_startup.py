#!/usr/bin/env python3
"""
Тест запуска сервера FSRS-only
"""
import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к app
sys.path.append(str(Path(__file__).parent / "app"))

async def test_server_startup():
    """Тест запуска сервера"""
    try:
        # Импортируем main модуль
        from app.main import app
        print("✅ FastAPI приложение успешно создано")
        
        # Проверяем роуты
        routes = [route.path for route in app.routes]
        print(f"🔍 Найдено роутов: {len(routes)}")
        
        # Проверяем ключевые роуты
        expected_routes = [
            "/fsrs/submit-answer",
            "/fsrs/submit-batch",
            "/fsrs/due-questions/{user_id}",
            "/fsrs/stats/{user_id}"
        ]
        
        for route in expected_routes:
            if route not in routes:
                print(f"❌ Отсутствует роут: {route}")
                return False
                
        print("✅ Все ключевые роуты присутствуют")
        
        print("\n🎉 Сервер готов к работе с FSRS-only системой!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server_startup())
    if success:
        print("\n✅ ТЕСТ ЗАПУСКА ПРОЙДЕН")
    else:
        print("\n❌ ТЕСТ ЗАПУСКА НЕ ПРОЙДЕН")
        sys.exit(1)
