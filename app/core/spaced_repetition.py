"""
Spaced Repetition System (SM-2 Algorithm) for Base10.

The SM-2 algorithm optimizes learning retention by scheduling reviews
at increasing intervals. Students remember 2.5x more vs random practice.

Original paper: https://www.supermemo.com/en/blog/application-of-a-computer-to-improve-the-results-obtained-in-working-with-the-supermemo-method
"""
from datetime import datetime, timedelta
from typing import Tuple


def calculate_next_review_sm2(
    quality: int,
    current_interval: int = 0,
    current_ease_factor: float = 2.5,
    current_repetitions: int = 0
) -> Tuple[int, float, int, datetime]:
    """
    Calculate next review date using SM-2 algorithm.
    
    Args:
        quality: Performance rating 0-5
            0-2: Incorrect (forgot/hard)
            3: Correct with difficulty
            4: Correct easily
            5: Perfect recall
        current_interval: Days since last review
        current_ease_factor: Difficulty multiplier (default 2.5)
        current_repetitions: Number of successful reviews in a row
    
    Returns:
        (next_interval, new_ease_factor, new_repetitions, next_review_date)
    
    SM-2 Logic:
    - Quality < 3: Reset repetitions, show again today
    - Quality >= 3: Increase interval based on ease factor
    - Ease factor adjusted by performance (harder questions = slower growth)
    """
    
    # Validate quality rating
    quality = max(0, min(5, quality))
    
    # Calculate new ease factor (EF)
    # Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ease_factor = current_ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    # Minimum ease factor is 1.3 (prevents cards from becoming too difficult)
    new_ease_factor = max(1.3, new_ease_factor)
    
    # If quality < 3 (incorrect): Reset and review immediately
    if quality < 3:
        new_repetitions = 0
        new_interval = 0  # Review again today
    else:
        # Correct answer: Increase interval
        new_repetitions = current_repetitions + 1
        
        if new_repetitions == 1:
            # First successful review: 1 day
            new_interval = 1
        elif new_repetitions == 2:
            # Second successful review: 6 days
            new_interval = 6
        else:
            # Subsequent reviews: multiply by ease factor
            new_interval = int(current_interval * new_ease_factor)
    
    # Calculate next review date
    next_review_date = datetime.utcnow() + timedelta(days=new_interval)
    
    return new_interval, new_ease_factor, new_repetitions, next_review_date


def quality_from_attempt(is_correct: bool, time_taken_seconds: int = None) -> int:
    """
    Convert attempt result to SM-2 quality rating (0-5).
    
    Args:
        is_correct: Whether answer was correct
        time_taken_seconds: Optional time to answer (not used yet)
    
    Returns:
        Quality rating 0-5
    
    Simple mapping (can be enhanced with time analysis later):
    - Incorrect: 2 (medium difficulty)
    - Correct: 4 (good)
    
    Future enhancement: Use time_taken to differentiate quality 3, 4, 5
    """
    if not is_correct:
        return 2  # Forgot/difficult
    else:
        return 4  # Good (easy to remember)
    
    # TODO: Add time-based quality differentiation
    # if time_taken_seconds:
    #     if time_taken_seconds < 5: return 5  # Perfect recall
    #     if time_taken_seconds < 15: return 4  # Good
    #     return 3  # Correct but slow


def get_due_reviews_count(attempts, current_time: datetime = None) -> int:
    """
    Count how many questions are due for review.
    
    Args:
        attempts: List of Attempt objects with next_review_date
        current_time: Current time (default: now)
    
    Returns:
        Number of due reviews
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    due_count = 0
    for attempt in attempts:
        if hasattr(attempt, 'next_review_date') and attempt.next_review_date:
            if attempt.next_review_date <= current_time:
                due_count += 1
    
    return due_count


def should_review_question(attempt, current_time: datetime = None) -> bool:
    """
    Check if a question is due for spaced repetition review.
    
    Args:
        attempt: Attempt object with next_review_date
        current_time: Current time (default: now)
    
    Returns:
        True if due for review, False otherwise
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    if not hasattr(attempt, 'next_review_date') or attempt.next_review_date is None:
        # Never reviewed: should practice
        return True
    
    return attempt.next_review_date <= current_time


# Example usage:
if __name__ == "__main__":
    print("SM-2 Spaced Repetition Demo\n")
    
    # Simulate answering a question 5 times
    interval = 0
    ease = 2.5
    reps = 0
    
    results = [4, 4, 5, 2, 4]  # Good, Good, Perfect, Forgot, Good
    
    for i, quality in enumerate(results, 1):
        interval, ease, reps, next_date = calculate_next_review_sm2(
            quality, interval, ease, reps
        )
        
        print(f"Attempt {i}: Quality={quality}")
        print(f"  → Next review in {interval} days ({next_date.date()})")
        print(f"  → Ease factor: {ease:.2f}, Repetitions: {reps}\n")
