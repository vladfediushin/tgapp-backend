#!/usr/bin/env python3
"""
Тест FSRS интеграции
"""
import sys
import os

# Добавляем backend в путь
sys.path.append('/Users/vladfediushin/MEGA/coding/tgapp_driving_final_v3/backend')

from app.schemas import BatchAnswerItem, BatchAnswersSubmit
from pydantic import ValidationError
import json

def test_fsrs_schemas():
    """Тестируем FSRS схемы"""
    print("🧪 Тестируем FSRS схемы...")
    
    # Тест 1: Обычный ответ без FSRS
    try:
        answer1 = BatchAnswerItem(
            question_id=123,
            is_correct=True,
            timestamp=1640995200000
        )
        print("✅ Обычный ответ: OK")
        print(f"   {answer1.dict()}")
    except Exception as e:
        print(f"❌ Обычный ответ: {e}")
    
    # Тест 2: FSRS ответ с полными данными
    try:
        answer2 = BatchAnswerItem(
            question_id=124,
            is_correct=True,
            timestamp=1640995200000,
            response_time=3500,  # 3.5 секунды
            difficulty_rating=3  # Good
        )
        print("✅ FSRS ответ: OK")
        print(f"   {answer2.dict()}")
    except Exception as e:
        print(f"❌ FSRS ответ: {e}")
    
    # Тест 3: Невалидный difficulty_rating
    try:
        answer3 = BatchAnswerItem(
            question_id=125,
            is_correct=False,
            difficulty_rating=5  # Невалидно (должно быть 1-4)
        )
        print("❌ Должна была быть ошибка валидации!")
    except ValidationError as e:
        print("✅ Валидация difficulty_rating: OK")
        print(f"   Ошибка: {e}")
    
    # Тест 4: Batch запрос
    try:
        batch = BatchAnswersSubmit(
            answers=[
                BatchAnswerItem(question_id=126, is_correct=True, response_time=2000, difficulty_rating=4),
                BatchAnswerItem(question_id=127, is_correct=False, response_time=5000, difficulty_rating=1),
                BatchAnswerItem(question_id=128, is_correct=True)  # Без FSRS данных
            ]
        )
        print("✅ Batch запрос: OK")
        print(f"   Количество ответов: {len(batch.answers)}")
        
        # Проверим JSON сериализацию
        json_data = batch.json()
        print(f"   JSON размер: {len(json_data)} символов")
        
    except Exception as e:
        print(f"❌ Batch запрос: {e}")

def test_fsrs_rating_mappings():
    """Тестируем маппинг FSRS рейтингов"""
    print("\n🔢 Тестируем FSRS рейтинги...")
    
    mappings = {
        1: "Again (Снова)",
        2: "Hard (Сложно)", 
        3: "Good (Хорошо)",
        4: "Easy (Легко)"
    }
    
    for rating, description in mappings.items():
        try:
            answer = BatchAnswerItem(
                question_id=100 + rating,
                is_correct=rating > 2,  # 3 и 4 = правильно, 1 и 2 = неправильно
                difficulty_rating=rating
            )
            print(f"✅ Рейтинг {rating} ({description}): OK")
        except Exception as e:
            print(f"❌ Рейтинг {rating}: {e}")

def test_automatic_rating_logic():
    """Тестируем логику автоматического рейтинга"""
    print("\n🤖 Тестируем автоматический рейтинг...")
    
    # Логика из frontend: правильный ответ = 4 (Easy), неправильный = 1 (Again)
    test_cases = [
        {"is_correct": True, "expected_rating": 4, "description": "Правильный → Easy"},
        {"is_correct": False, "expected_rating": 1, "description": "Неправильный → Again"}
    ]
    
    for case in test_cases:
        auto_rating = 4 if case["is_correct"] else 1
        
        answer = BatchAnswerItem(
            question_id=200,
            is_correct=case["is_correct"],
            difficulty_rating=auto_rating
        )
        
        if auto_rating == case["expected_rating"]:
            print(f"✅ {case['description']}: OK (рейтинг {auto_rating})")
        else:
            print(f"❌ {case['description']}: Ожидали {case['expected_rating']}, получили {auto_rating}")

if __name__ == "__main__":
    print("🚀 Запуск тестов FSRS интеграции\n")
    
    try:
        test_fsrs_schemas()
        test_fsrs_rating_mappings()
        test_automatic_rating_logic()
        
        print("\n🎉 Все тесты завершены!")
        
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
