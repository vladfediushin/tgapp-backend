# 🧠 FSRS Algorithm Integration

## Overview
This project now includes a complete integration of the FSRS-6 (Free Spaced Repetition Scheduler) algorithm for optimized learning and retention. FSRS is a modern, scientifically-backed spaced repetition algorithm that significantly improves upon traditional methods.

## 🎯 Key Features

### Backend (Python/FastAPI)
- **FSRS-6 Library Integration**: Using the official `fsrs` Python library
- **Enhanced Database Schema**: 10 new FSRS-specific fields in UserProgress
- **FSRS Service Layer**: Complete abstraction for FSRS operations
- **API Endpoints**: Dedicated `/fsrs/` routes for FSRS functionality
- **Batch Processing**: Efficient batch submission with FSRS ratings

### Frontend (React/TypeScript)
- **FSRS Store**: Zustand-based state management with persistence
- **Type-Safe API Client**: Complete TypeScript integration
- **Interactive Dashboard**: Real-time FSRS statistics and insights
- **Test Interface**: Comprehensive testing and validation tools
- **Auto-Rating System**: Intelligent rating calculation based on performance

## 📊 FSRS Algorithm Benefits

### Traditional Fibonacci vs FSRS
- **Old System**: Fixed Fibonacci intervals (1, 1, 2, 3, 5, 8, 13...)
- **FSRS System**: Dynamic intervals based on:
  - Card stability (how well you know it)
  - Card difficulty (inherent complexity)
  - Your performance history
  - Forgetting curve modeling

### Performance Improvements
- **Retention Rate**: Up to 95% retention with optimal intervals
- **Study Time**: Reduced by 30-50% compared to traditional methods
- **Long-term Memory**: Better consolidation through scientific spacing
- **Personalization**: Adapts to individual learning patterns

## 🛠️ Technical Implementation

### Database Schema
```sql
-- New FSRS fields added to user_progress table
ALTER TABLE user_progress ADD COLUMN stability FLOAT;
ALTER TABLE user_progress ADD COLUMN difficulty FLOAT;
ALTER TABLE user_progress ADD COLUMN retrievability FLOAT;
ALTER TABLE user_progress ADD COLUMN elapsed_days INTEGER;
ALTER TABLE user_progress ADD COLUMN scheduled_days INTEGER;
ALTER TABLE user_progress ADD COLUMN reps INTEGER;
ALTER TABLE user_progress ADD COLUMN lapses INTEGER;
ALTER TABLE user_progress ADD COLUMN state INTEGER;
ALTER TABLE user_progress ADD COLUMN last_review TIMESTAMPTZ;
ALTER TABLE user_progress ADD COLUMN due TIMESTAMPTZ;
```

### FSRS Rating System
```
1 = Again    (Incorrect answer - need to review soon)
2 = Hard     (Correct but difficult - shorter interval)
3 = Good     (Correct with normal effort - standard interval)
4 = Easy     (Correct with ease - longer interval)
```

### API Endpoints
```
POST /fsrs/submit-answer       - Submit single answer with FSRS rating
POST /fsrs/submit-batch        - Submit multiple answers with ratings
GET  /fsrs/due-questions/{id}  - Get questions due for review
GET  /fsrs/stats/{id}          - Get FSRS statistics for user
GET  /fsrs/card-info/{id}/{qid} - Get detailed card information
```

## 🚀 Usage Examples

### Backend (Python)
```python
from app.services.fsrs_service import fsrs_service

# Schedule a review
progress_data = fsrs_service.schedule_review(
    progress=user_progress,
    rating=3,  # Good
    review_time=datetime.now()
)

# Get due status
due_info = fsrs_service.get_card_due_status(user_progress)
```

### Frontend (TypeScript)
```typescript
import { useFSRSActions } from '../store/fsrs'

const { addAnswer, submitPendingAnswers } = useFSRSActions()

// Add answer with auto-rating
addAnswer(questionId, isCorrect, responseTime)

// Submit to FSRS backend
await submitPendingAnswers(userId)
```

## 📈 FSRS States
- **New (0)**: Never reviewed
- **Learning (1)**: Being learned, short intervals
- **Review (2)**: In long-term memory, longer intervals  
- **Relearning (3)**: Forgotten, needs relearning

## 🔧 Configuration

### Backend Settings
```python
# app/services/fsrs_service.py
fsrs = Scheduler()  # Uses default FSRS-6 parameters
```

### Frontend Settings
```typescript
interface FSRSSettings {
  enabled: boolean          // Enable/disable FSRS
  autoRating: boolean      // Auto-calculate ratings
  showIntervals: boolean   // Show predicted intervals
  showStats: boolean       // Show statistics dashboard
}
```

## 🧪 Testing

### FSRS Test Page
Navigate to `/test-fsrs` (in development) to access:
- FSRS settings configuration
- Test answer generation
- Pending answers management
- Real-time statistics dashboard
- User info and debugging

### Example Test Flow
1. Configure FSRS settings
2. Generate test answers with various performance levels
3. Submit answers to FSRS backend
4. Observe statistics and interval predictions
5. Validate scheduling accuracy

## 📚 Scientific Background

FSRS is based on:
- **Three-Component Model of Memory**: Stability, Retrievability, Difficulty
- **Forgetting Curve**: Exponential decay model
- **Spacing Effect**: Optimal intervals for long-term retention
- **Difficulty Effect**: Harder items need different scheduling

### Key Papers
- Piotr Woźniak's SuperMemo research
- Hermann Ebbinghaus forgetting curve
- Robert Bjork's desirable difficulties theory

## 🔄 Migration Strategy

### Backward Compatibility
- Legacy Fibonacci system still available
- FSRS can be enabled/disabled per user
- Gradual migration possible
- No data loss during transition

### Migration Process
1. Run Alembic migration to add FSRS fields
2. Deploy backend with FSRS endpoints
3. Deploy frontend with FSRS components
4. Enable FSRS for test users
5. Monitor performance and adjust
6. Roll out to all users

## 🐛 Troubleshooting

### Common Issues
1. **ImportError: FSRS**: Ensure `fsrs==6.1.0` is installed
2. **Database Migration**: Run `alembic upgrade head`
3. **API Errors**: Check FSRS rating values (1-4)
4. **Frontend Errors**: Verify Zod schema validation

### Debug Commands
```bash
# Backend
python -c "from app.services.fsrs_service import fsrs_service; print('FSRS OK')"

# Frontend  
npm run build  # Should complete without errors
```

## 📊 Performance Monitoring

### Metrics to Track
- Average retention rate
- Study time per session
- Interval accuracy
- User satisfaction
- Memory consolidation

### Dashboard Insights
- Total cards in system
- Cards due for review
- Average stability/difficulty
- State distribution
- Learning progress trends

## 🔮 Future Enhancements

### Planned Features
- **Custom FSRS Parameters**: User-specific algorithm tuning
- **Advanced Analytics**: Detailed learning pattern analysis
- **A/B Testing**: Compare FSRS vs traditional methods
- **Mobile Optimization**: Enhanced mobile experience
- **Bulk Operations**: Admin tools for managing FSRS data

### Research Opportunities
- Learning pattern analysis
- Optimal parameter discovery
- Cultural/language-specific adjustments
- Integration with cognitive load theory

## 📖 References
- [FSRS-6 Paper](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm)
- [FSRS Python Library](https://github.com/open-spaced-repetition/py-fsrs)
- [Spaced Repetition Research](https://gwern.net/spaced-repetition)
- [SuperMemo Algorithm](https://supermemo.guru/wiki/Algorithm_SM-2)

---

*The FSRS integration represents a significant advancement in our learning platform, providing users with scientifically-optimized spaced repetition that adapts to their individual learning patterns and maximizes long-term retention.*
