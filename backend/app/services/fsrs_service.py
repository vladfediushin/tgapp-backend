"""
FSRS Service Layer
Provides integration with FSRS-6 spaced repetition algorithm
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fsrs import Scheduler, Card, Rating, ReviewLog, State
from app.models import UserProgress


class FSRSService:
    """Service for FSRS algorithm integration"""
    
    def __init__(self):
        """Initialize FSRS scheduler with default parameters"""
        self.fsrs = Scheduler()
    
    def convert_progress_to_card(self, progress: UserProgress) -> Card:
        """
        Convert UserProgress database record to FSRS Card object
        
        Args:
            progress: UserProgress database record
            
        Returns:
            Card: FSRS Card object for scheduling
        """
        # Determine card state from progress data
        if progress.state is None:
            # New card - never reviewed
            state = State.New
        else:
            # Convert integer state to FSRS State enum
            state = State(progress.state)
        
        # Convert timestamps to proper timezone-aware datetime objects
        last_review = None
        due = None
        
        if progress.last_review:
            if progress.last_review.tzinfo is None:
                last_review = progress.last_review.replace(tzinfo=timezone.utc)
            else:
                last_review = progress.last_review
        
        if progress.due:
            if progress.due.tzinfo is None:
                due = progress.due.replace(tzinfo=timezone.utc)
            else:
                due = progress.due
        
        # Create FSRS Card with existing progress data
        card = Card(
            due=due or datetime.now(timezone.utc),
            stability=progress.stability,
            difficulty=progress.difficulty,
            state=state,
            last_review=last_review
        )
        
        return card
    
    def convert_card_to_progress_data(self, card: Card) -> Dict[str, Any]:
        """
        Convert FSRS Card object back to UserProgress fields
        
        Args:
            card: FSRS Card object
            
        Returns:
            Dict with UserProgress field updates
        """
        return {
            'stability': card.stability,
            'difficulty': card.difficulty,
            'state': card.state.value,  # Convert enum to integer
            'last_review': card.last_review,
            'due': card.due,
            # Note: FSRS Card doesn't have these fields, so we'll manage them separately
            'elapsed_days': 0,  # Will be calculated separately
            'scheduled_days': 0,  # Will be calculated separately
            'reps': 0,  # Will be managed in CRUD
            'lapses': 0,  # Will be managed in CRUD
            'retrievability': None  # Will be calculated if needed
        }
    
    def schedule_review(self, progress: UserProgress, rating: int, review_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Schedule next review using FSRS algorithm
        
        Args:
            progress: Current UserProgress record
            rating: User rating (1=Again, 2=Hard, 3=Good, 4=Easy)
            review_time: Time of review (defaults to now)
            
        Returns:
            Dict with updated progress fields
        """
        if review_time is None:
            review_time = datetime.now(timezone.utc)
        elif review_time.tzinfo is None:
            review_time = review_time.replace(tzinfo=timezone.utc)
        
        # Convert progress to FSRS Card
        card = self.convert_progress_to_card(progress)
        
        # Convert rating to FSRS Rating enum
        fsrs_rating = Rating(rating)
        
        # Schedule the review
        updated_card, review_log = self.fsrs.review_card(card, fsrs_rating, review_time)
        
        # Convert back to progress data
        return self.convert_card_to_progress_data(updated_card)
    
    def get_card_due_status(self, progress: UserProgress, current_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Check if a card is due for review
        
        Args:
            progress: UserProgress record to check
            current_time: Current time (defaults to now)
            
        Returns:
            Dict with due status information
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        elif current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        
        card = self.convert_progress_to_card(progress)
        
        is_due = card.due <= current_time
        
        return {
            'is_due': is_due,
            'due_date': card.due,
            'days_until_due': (card.due - current_time).days if not is_due else 0,
            'state': card.state.name,
            'stability': card.stability,
            'difficulty': card.difficulty
        }
    
    def get_next_intervals(self, progress: UserProgress) -> Dict[str, Dict[str, Any]]:
        """
        Get predicted intervals for all possible ratings
        
        Args:
            progress: Current UserProgress record
            
        Returns:
            Dict mapping rating names to predicted outcomes
        """
        card = self.convert_progress_to_card(progress)
        current_time = datetime.now(timezone.utc)
        
        results = {}
        rating_names = {
            Rating.Again: 'again',
            Rating.Hard: 'hard', 
            Rating.Good: 'good',
            Rating.Easy: 'easy'
        }
        
        # Get all possible outcomes by testing each rating
        for rating in Rating:
            scheduled_card, _ = self.fsrs.review_card(card, rating, current_time)
            interval_days = (scheduled_card.due - current_time).days
            
            results[rating_names[rating]] = {
                'interval_days': interval_days,
                'due_date': scheduled_card.due,
                'stability': scheduled_card.stability,
                'difficulty': scheduled_card.difficulty,
                'state': scheduled_card.state.name
            }
        
        return results


# Global FSRS service instance
fsrs_service = FSRSService()
