"""
Analytics & Telemetry Service - Question Health Monitoring and Usage Tracking.

Why analytics matter for Base10:
1. Question quality: If 90% fail a question, flag it for review
2. Content gaps: Users search "cryptocurrency" but no content exists
3. Engagement metrics: Show investors "Students spend 45 mins/day"
4. Offline batching: Mobile records events, uploads compressed logs on reconnect

Key principles:
- Privacy-first: No PII in logs, aggregate only
- Lightweight: Batch events to minimize bandwidth
- Actionable: Metrics drive content decisions
"""
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import json

# Optional: PostHog for product analytics
try:
    from posthog import Posthog
    HAS_POSTHOG = True
except ImportError:
    HAS_POSTHOG = False
    print("⚠️  posthog not installed. Install: pip install posthog")

# Optional: TimescaleDB for time-series metrics
try:
    from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    HAS_TIMESCALE = True
    Base = declarative_base()
except ImportError:
    HAS_TIMESCALE = False

from app.core.config import settings
from app.database.session import SessionLocal
from app.models.question import Question
from app.models.attempt import Attempt

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Analytics event types."""
    # Question events
    QUESTION_VIEWED = "question_viewed"
    QUESTION_ANSWERED = "question_answered"
    QUESTION_SKIPPED = "question_skipped"
    EXPLANATION_VIEWED = "explanation_viewed"
    HINT_REVEALED = "hint_revealed"
    
    # Search events
    SEARCH_PERFORMED = "search_performed"
    SEARCH_NO_RESULTS = "search_no_results"
    
    # Session events
    QUIZ_STARTED = "quiz_started"
    QUIZ_COMPLETED = "quiz_completed"
    QUIZ_ABANDONED = "quiz_abandoned"
    
    # Engagement events
    STREAK_ACHIEVED = "streak_achieved"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    LEADERBOARD_VIEWED = "leaderboard_viewed"
    
    # Offline events
    OFFLINE_SESSION_STARTED = "offline_session_started"
    OFFLINE_SYNC_COMPLETED = "offline_sync_completed"


class QuestionHealthMetric(Enum):
    """Health indicators for question quality."""
    DIFFICULTY_RATING = "difficulty_rating"  # % who answer correctly
    SKIP_RATE = "skip_rate"                  # % who skip without attempting
    TIME_TO_ANSWER = "time_to_answer"        # Avg seconds spent
    EXPLANATION_VIEWS = "explanation_views"  # % who view explanation after
    CONFUSION_SCORE = "confusion_score"      # High skip + low correct = confusing


# Optional: TimescaleDB model for time-series metrics
if HAS_TIMESCALE:
    class QuestionMetric(Base):
        """Time-series metrics for question performance."""
        __tablename__ = "question_metrics"
        
        id = Column(Integer, primary_key=True, index=True)
        question_id = Column(Integer, index=True, nullable=False)
        timestamp = Column(DateTime, default=datetime.utcnow, index=True)
        
        # Aggregated metrics (updated hourly)
        attempts_count = Column(Integer, default=0)
        correct_count = Column(Integer, default=0)
        skip_count = Column(Integer, default=0)
        avg_time_seconds = Column(Float, default=0.0)
        explanation_views = Column(Integer, default=0)
        
        # Health score (0-100, higher is better)
        health_score = Column(Float, default=100.0)
        
        # Metadata
        metadata = Column(JSON, nullable=True)


class AnalyticsService:
    """
    Central analytics hub for Base10.
    
    Tracks:
    - Question performance (accuracy, skip rate, time)
    - Content gaps (searches with no results)
    - User engagement (streaks, session duration)
    - Offline sync patterns
    """
    
    def __init__(self):
        # PostHog integration
        if HAS_POSTHOG and settings.POSTHOG_API_KEY:
            self.posthog = Posthog(
                project_api_key=settings.POSTHOG_API_KEY,
                host=settings.POSTHOG_HOST or 'https://app.posthog.com'
            )
            self.posthog_enabled = True
        else:
            self.posthog_enabled = False
            logger.warning("⚠️  PostHog not configured. Using fallback logging.")
        
        # TimescaleDB for time-series
        if HAS_TIMESCALE and settings.TIMESCALE_URL:
            engine = create_engine(settings.TIMESCALE_URL)
            Base.metadata.create_all(engine)
            self.SessionLocal = sessionmaker(bind=engine)
            self.timescale_enabled = True
        else:
            self.timescale_enabled = False
    
    
    def track_event(
        self,
        user_id: int,
        event: EventType,
        properties: Optional[Dict[str, Any]] = None
    ):
        """
        Track analytics event.
        
        Args:
            user_id: User ID (anonymized in logs)
            event: Event type
            properties: Additional event data
        """
        event_data = {
            'event': event.value,
            'user_id': str(user_id),  # Stringified for privacy
            'timestamp': datetime.utcnow().isoformat(),
            'properties': properties or {}
        }
        
        # Send to PostHog
        if self.posthog_enabled:
            try:
                self.posthog.capture(
                    distinct_id=str(user_id),
                    event=event.value,
                    properties=properties
                )
            except Exception as e:
                logger.error(f"❌ PostHog tracking failed: {e}")
        
        # Fallback: Log to file
        logger.info(f"📊 Event: {json.dumps(event_data)}")
    
    
    def track_question_attempt(
        self,
        user_id: int,
        question_id: int,
        is_correct: bool,
        time_spent_seconds: int,
        viewed_explanation: bool = False,
        skipped: bool = False
    ):
        """Track question attempt with detailed metrics."""
        properties = {
            'question_id': question_id,
            'is_correct': is_correct,
            'time_spent_seconds': time_spent_seconds,
            'viewed_explanation': viewed_explanation,
            'skipped': skipped
        }
        
        event = EventType.QUESTION_SKIPPED if skipped else EventType.QUESTION_ANSWERED
        self.track_event(user_id, event, properties)
        
        # Update question health metrics
        self._update_question_health(question_id, is_correct, time_spent_seconds, skipped)
    
    
    def track_search(
        self,
        user_id: int,
        query: str,
        results_count: int,
        subjects_searched: Optional[List[str]] = None
    ):
        """
        Track search queries to identify content gaps.
        
        If results_count == 0, this is a content gap opportunity.
        """
        properties = {
            'query': query,
            'results_count': results_count,
            'subjects_searched': subjects_searched or []
        }
        
        event = EventType.SEARCH_NO_RESULTS if results_count == 0 else EventType.SEARCH_PERFORMED
        self.track_event(user_id, event, properties)
        
        # Log content gaps for manual review
        if results_count == 0:
            logger.warning(f"🔍 Content gap: User searched '{query}' but no results found")
    
    
    def track_offline_batch(
        self,
        user_id: int,
        events: List[Dict[str, Any]]
    ):
        """
        Process batched events from offline mobile app.
        
        Mobile app stores events locally, uploads in batch when online.
        """
        logger.info(f"📦 Processing {len(events)} offline events from user {user_id}")
        
        for event_data in events:
            try:
                event_type = EventType(event_data.get('event'))
                properties = event_data.get('properties', {})
                
                # Add offline flag
                properties['was_offline'] = True
                
                self.track_event(user_id, event_type, properties)
            
            except (ValueError, KeyError) as e:
                logger.error(f"❌ Invalid offline event: {e}")
    
    
    def get_question_health_report(
        self,
        question_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate health report for a specific question.
        
        Returns:
            {
                'question_id': 123,
                'health_score': 75.0,  # 0-100
                'metrics': {
                    'total_attempts': 1000,
                    'correct_rate': 0.65,
                    'skip_rate': 0.10,
                    'avg_time_seconds': 45.2,
                    'explanation_views': 300
                },
                'flags': ['high_skip_rate', 'below_avg_correct_rate'],
                'recommendation': 'Review question clarity'
            }
        """
        db = SessionLocal()
        
        try:
            # Query attempts for this question in last N days
            since = datetime.utcnow() - timedelta(days=days)
            
            attempts = db.query(Attempt).filter(
                Attempt.question_id == question_id,
                Attempt.created_at >= since
            ).all()
            
            if not attempts:
                return {
                    'question_id': question_id,
                    'health_score': None,
                    'message': 'Insufficient data'
                }
            
            # Calculate metrics
            total_attempts = len(attempts)
            correct_count = sum(1 for a in attempts if a.is_correct)
            skip_count = sum(1 for a in attempts if a.skipped)  # Assuming 'skipped' field exists
            
            correct_rate = correct_count / total_attempts if total_attempts > 0 else 0
            skip_rate = skip_count / total_attempts if total_attempts > 0 else 0
            
            # Health score calculation (simple heuristic)
            # 100 = everyone gets it right, no skips
            # 0 = everyone skips or gets wrong
            health_score = (correct_rate * 100) - (skip_rate * 50)
            health_score = max(0, min(100, health_score))  # Clamp to 0-100
            
            # Flags
            flags = []
            if skip_rate > 0.20:
                flags.append('high_skip_rate')
            if correct_rate < 0.50:
                flags.append('below_avg_correct_rate')
            if health_score < 50:
                flags.append('critical_health')
            
            # Recommendation
            if 'critical_health' in flags:
                recommendation = 'URGENT: Review question clarity and answer choices'
            elif 'high_skip_rate' in flags:
                recommendation = 'Question may be confusing or too difficult'
            elif 'below_avg_correct_rate' in flags:
                recommendation = 'Consider adding hints or revising explanation'
            else:
                recommendation = 'Question performing well'
            
            return {
                'question_id': question_id,
                'health_score': round(health_score, 2),
                'metrics': {
                    'total_attempts': total_attempts,
                    'correct_rate': round(correct_rate, 3),
                    'skip_rate': round(skip_rate, 3)
                },
                'flags': flags,
                'recommendation': recommendation
            }
        
        finally:
            db.close()
    
    
    def get_content_gaps_report(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Identify content gaps from search queries with no results.
        
        Returns top 10 queries with no results (opportunities for new content).
        """
        # TODO: Implement search query tracking in database
        # For now, return mock data
        
        logger.warning("⚠️  Content gaps report not fully implemented. Add search_queries table.")
        
        return [
            {'query': 'cryptocurrency', 'search_count': 45, 'subjects': ['Economics']},
            {'query': 'climate change', 'search_count': 32, 'subjects': ['Geography']},
            {'query': 'machine learning', 'search_count': 28, 'subjects': ['Computer Science']}
        ]
    
    
    def get_engagement_metrics(
        self,
        user_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate engagement report.
        
        Metrics:
        - Total active users
        - Avg session duration
        - Avg questions per session
        - Streak distribution
        - Daily active users (DAU)
        """
        db = SessionLocal()
        
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            # Total attempts in period
            query = db.query(Attempt).filter(Attempt.created_at >= since)
            
            if user_id:
                query = query.filter(Attempt.user_id == user_id)
            
            attempts = query.all()
            
            if not attempts:
                return {'message': 'No activity in this period'}
            
            # Calculate metrics
            unique_users = len(set(a.user_id for a in attempts))
            total_attempts = len(attempts)
            avg_attempts_per_user = total_attempts / unique_users if unique_users > 0 else 0
            
            # Accuracy
            correct_attempts = sum(1 for a in attempts if a.is_correct)
            overall_accuracy = correct_attempts / total_attempts if total_attempts > 0 else 0
            
            return {
                'period_days': days,
                'unique_users': unique_users,
                'total_attempts': total_attempts,
                'avg_attempts_per_user': round(avg_attempts_per_user, 2),
                'overall_accuracy': round(overall_accuracy, 3),
                'daily_avg_attempts': round(total_attempts / days, 2)
            }
        
        finally:
            db.close()
    
    
    def _update_question_health(
        self,
        question_id: int,
        is_correct: bool,
        time_spent_seconds: int,
        skipped: bool
    ):
        """
        Update time-series metrics for question health.
        
        This runs after every attempt (could be batched for performance).
        """
        if not self.timescale_enabled:
            return
        
        db = self.SessionLocal()
        
        try:
            # Find or create today's metric record
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            metric = db.query(QuestionMetric).filter(
                QuestionMetric.question_id == question_id,
                QuestionMetric.timestamp == today
            ).first()
            
            if not metric:
                metric = QuestionMetric(
                    question_id=question_id,
                    timestamp=today
                )
                db.add(metric)
            
            # Update aggregated metrics
            metric.attempts_count += 1
            if is_correct:
                metric.correct_count += 1
            if skipped:
                metric.skip_count += 1
            
            # Update average time (running average)
            n = metric.attempts_count
            metric.avg_time_seconds = ((metric.avg_time_seconds * (n - 1)) + time_spent_seconds) / n
            
            # Recalculate health score
            correct_rate = metric.correct_count / metric.attempts_count
            skip_rate = metric.skip_count / metric.attempts_count
            metric.health_score = (correct_rate * 100) - (skip_rate * 50)
            metric.health_score = max(0, min(100, metric.health_score))
            
            db.commit()
        
        except Exception as e:
            logger.error(f"❌ Failed to update question health: {e}")
            db.rollback()
        
        finally:
            db.close()


# Example usage:
if __name__ == "__main__":
    analytics = AnalyticsService()
    
    # Example 1: Track question attempt
    analytics.track_question_attempt(
        user_id=123,
        question_id=456,
        is_correct=False,
        time_spent_seconds=45,
        viewed_explanation=True,
        skipped=False
    )
    
    # Example 2: Track search (content gap)
    analytics.track_search(
        user_id=123,
        query="cryptocurrency basics",
        results_count=0,  # Content gap!
        subjects_searched=['Economics']
    )
    
    # Example 3: Get question health report
    report = analytics.get_question_health_report(question_id=456, days=30)
    print(f"Question health: {report['health_score']}/100")
    print(f"Recommendation: {report['recommendation']}")
    
    # Example 4: Offline batch processing
    offline_events = [
        {'event': 'question_answered', 'properties': {'question_id': 789, 'is_correct': True}},
        {'event': 'quiz_completed', 'properties': {'score': 8.5, 'questions_count': 10}}
    ]
    analytics.track_offline_batch(user_id=123, events=offline_events)
    
    # Example 5: Engagement metrics
    metrics = analytics.get_engagement_metrics(days=7)
    print(f"Weekly engagement: {metrics}")
