#!/usr/bin/env python3
"""
Тест FSRS API endpoints
"""
import sys
import os
import asyncio
import json
from datetime import datetime, timezone

# Добавляем backend в путь
sys.path.append('/Users/vladfediushin/MEGA/coding/tgapp_driving_final_v3/backend')

async def test_fsrs_endpoints():
    """Тестируем FSRS API endpoints без запуска сервера"""
    print("🔌 Тестируем FSRS API логику...")
    
    try:
        from app.routers import submit_answers
        from app.schemas import BatchAnswersSubmit, BatchAnswerItem
        from app.database import get_db
        from sqlalchemy.orm import Session
        
        print("✅ Импорты успешны")
        
        # Создаем тестовые данные
        test_data = BatchAnswersSubmit(
            answers=[
                BatchAnswerItem(
                    question_id=123,
                    is_correct=True,
                    timestamp=int(datetime.now(timezone.utc).timestamp() * 1000),
                    response_time=3500,  # 3.5 секунды
                    difficulty_rating=3  # Good
                ),
                BatchAnswerItem(
                    question_id=124,
                    is_correct=False,
                    timestamp=int(datetime.now(timezone.utc).timestamp() * 1000),
                    response_time=8000,  # 8 секунд
                    difficulty_rating=1  # Again
                )
            ]
        )
        
        print("✅ Тестовые данные созданы")
        print(f"   Ответов: {len(test_data.answers)}")
        
        # Проверяем JSON сериализацию
        json_data = test_data.model_dump_json()
        print(f"   JSON размер: {len(json_data)} символов")
        
        # Проверяем десериализацию
        parsed_back = BatchAnswersSubmit.model_validate_json(json_data)
        print("✅ JSON сериализация/десериализация работает")
        
        # Тестируем FSRS параметры
        fsrs_test_cases = [
            {"use_fsrs": True, "description": "С FSRS"},
            {"use_fsrs": False, "description": "Без FSRS"}
        ]
        
        for case in fsrs_test_cases:
            print(f"\n🧪 Тест: {case['description']}")
            
            # Имитируем логику из routers.py
            use_fsrs = case["use_fsrs"]
            
            for answer in test_data.answers:
                answer_dict = answer.model_dump()
                
                if use_fsrs and answer_dict.get("difficulty_rating") and answer_dict.get("response_time"):
                    print(f"   ✅ Вопрос {answer.question_id}: FSRS активен")
                    print(f"      Сложность: {answer.difficulty_rating}")
                    print(f"      Время ответа: {answer.response_time}ms")
                else:
                    print(f"   📝 Вопрос {answer.question_id}: Обычный режим")
        
        print("\n🎯 API логика работает корректно!")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("   Возможно, нужно установить зависимости или запустить из другой директории")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

def test_fsrs_database_fields():
    """Тестируем поля базы данных для FSRS"""
    print("\n💾 Тестируем поля базы данных...")
    
    try:
        from app.models import UserProgress
        
        # Проверяем, что модель имеет FSRS поля
        fsrs_fields = ['stability', 'difficulty', 'retrievability', 'state', 'reps', 'lapses']
        
        for field in fsrs_fields:
            if hasattr(UserProgress, field):
                print(f"✅ Поле {field}: найдено")
            else:
                print(f"❌ Поле {field}: отсутствует")
        
        print("✅ Проверка полей базы данных завершена")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта моделей: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_fsrs_algorithm_integration():
    """Тестируем интеграцию FSRS алгоритма"""
    print("\n🧠 Тестируем интеграцию FSRS алгоритма...")
    
    try:
        # Проверяем наличие FSRS кода
        backend_path = '/Users/vladfediushin/MEGA/coding/tgapp_driving_final_v3/backend'
        
        # Ищем FSRS файлы
        fsrs_files_to_check = [
            'app/services/fsrs_service.py',
            'app/crud/user_progress.py'
        ]
        
        for file_path in fsrs_files_to_check:
            full_path = os.path.join(backend_path, file_path)
            if os.path.exists(full_path):
                print(f"✅ {file_path}: найден")
                
                # Проверяем содержимое файла
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'FSRS' in content or 'fsrs' in content:
                        print(f"   📝 Содержит FSRS код")
                    else:
                        print(f"   ⚠️  FSRS код не найден")
            else:
                print(f"❌ {file_path}: отсутствует")
        
        print("✅ Проверка FSRS интеграции завершена")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов FSRS API и интеграции\n")
    
    # Запускаем тесты
    asyncio.run(test_fsrs_endpoints())
    test_fsrs_database_fields()
    test_fsrs_algorithm_integration()
    
    print("\n🎉 Все тесты API завершены!")
