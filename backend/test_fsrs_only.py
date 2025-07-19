#!/usr/bin/env python3
"""
Тест системы FSRS-only после удаления логики Fibonacci
"""
import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к app
sys.path.append(str(Path(__file__).parent / "app"))

async def test_fsrs_system():
    """Тест FSRS системы"""
    try:
        # Импортируем модули по отдельности
        import app.crud.user_progress as crud_progress
        from app.models import UserProgress
        
        print("✅ Все модули успешно импортированы")
        
        # Проверяем, что модель UserProgress содержит только FSRS поля
        progress_fields = [attr for attr in dir(UserProgress) if not attr.startswith('_') and not callable(getattr(UserProgress, attr))]
        print(f"🔍 Поля модели UserProgress: {progress_fields}")
        
        # Проверяем наличие FSRS полей
        required_fsrs_fields = ['stability', 'difficulty', 'retrievability', 'state', 'reps', 'lapses', 'due']
        missing_fields = [field for field in required_fsrs_fields if not hasattr(UserProgress, field)]
        if missing_fields:
            print(f"❌ Отсутствуют FSRS поля: {missing_fields}")
            return False
            
        # Проверяем отсутствие старых полей
        old_fields = ['repetition_count', 'next_due_at']
        present_old_fields = [field for field in old_fields if hasattr(UserProgress, field)]
        if present_old_fields:
            print(f"❌ Остались старые поля: {present_old_fields}")
            return False
            
        print("✅ Модель UserProgress содержит только FSRS поля")
        
        # Проверяем функции CRUD
        crud_functions = [
            'create_or_update_progress',
            'create_or_update_progress_batch',
            'get_progress_for_user',
            'get_user_progress_for_question',
            'get_due_questions'
        ]
        
        for func_name in crud_functions:
            if not hasattr(crud_progress, func_name):
                print(f"❌ Отсутствует функция: {func_name}")
                return False
                
        print("✅ Все CRUD функции присутствуют")
        
        # Проверяем отсутствие старых функций
        old_functions = [
            'create_or_update_progress_fsrs', 
            'create_or_update_progress_batch_fsrs',
            'calculate_next_due_date',
            'FIB_SEQUENCE'
        ]
        
        for func_name in old_functions:
            if hasattr(crud_progress, func_name):
                print(f"❌ Остался старый элемент: {func_name}")
                return False
                
        print("✅ Старые функции Fibonacci удалены")
        
        print("\n🎉 Все проверки пройдены! Система работает только с FSRS")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fsrs_system())
    if success:
        print("\n✅ ТЕСТ ПРОЙДЕН: Система успешно переведена на FSRS-only")
    else:
        print("\n❌ ТЕСТ НЕ ПРОЙДЕН: Обнаружены проблемы")
        sys.exit(1)
