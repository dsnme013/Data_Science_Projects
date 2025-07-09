from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models import models, schemas
from app.models.models import MasteryLevel, DifficultyLevel
import json

class AnalyticsService:
    
    @staticmethod
    def start_session(db: Session, user_id: int, topic_id: Optional[int] = None, 
                     device_info: Optional[Dict[str, Any]] = None) -> models.SessionAnalytics:
        """Start a new session for tracking."""
        session = models.SessionAnalytics(
            user_id=user_id,
            topic_id=topic_id,
            device_info=device_info,
            session_start=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def end_session(db: Session, session_id: int, actions_taken: Optional[List[Dict[str, Any]]] = None):
        """End a session and calculate duration."""
        session = db.query(models.SessionAnalytics).filter(
            models.SessionAnalytics.id == session_id
        ).first()
        
        if session:
            session.session_end = datetime.utcnow()
            session.duration_minutes = (session.session_end - session.session_start).total_seconds() / 60
            if actions_taken:
                session.actions_taken = actions_taken
            db.commit()
    
    @staticmethod
    def track_time_on_topic(db: Session, user_id: int, topic_id: int, time_spent_minutes: float):
        """Track time spent on a specific topic."""
        # Get or create user progress
        progress = db.query(models.UserProgress).filter(
            and_(models.UserProgress.user_id == user_id, 
                 models.UserProgress.topic_id == topic_id)
        ).first()
        
        if not progress:
            progress = models.UserProgress(
                user_id=user_id,
                topic_id=topic_id,
                started_at=datetime.utcnow()
            )
            db.add(progress)
        
        progress.time_spent_minutes += time_spent_minutes
        progress.last_accessed = datetime.utcnow()
        db.commit()
        db.refresh(progress)
        return progress
    
    @staticmethod
    def calculate_mastery_level(db: Session, user_id: int, topic_id: int) -> MasteryLevel:
        """Calculate mastery level based on user performance."""
        # Get all user answers for this topic's checkpoints
        topic_checkpoints = db.query(models.Checkpoint).filter(
            models.Checkpoint.topic_id == topic_id
        ).all()
        
        checkpoint_ids = [cp.id for cp in topic_checkpoints]
        
        user_answers = db.query(models.UserAnswer).filter(
            and_(
                models.UserAnswer.user_id == user_id,
                models.UserAnswer.checkpoint_id.in_(checkpoint_ids)
            )
        ).all()
        
        if not user_answers:
            return MasteryLevel.NOT_STARTED
        
        # Calculate accuracy
        correct_answers = sum(1 for answer in user_answers if answer.is_correct)
        total_answers = len(user_answers)
        accuracy = correct_answers / total_answers if total_answers > 0 else 0
        
        # Calculate average time performance
        avg_time = sum(answer.time_taken_seconds or 0 for answer in user_answers) / total_answers
        
        # Get expected time for checkpoints
        expected_times = [cp.time_limit_seconds for cp in topic_checkpoints]
        avg_expected_time = sum(expected_times) / len(expected_times) if expected_times else 60
        
        time_factor = min(avg_expected_time / avg_time, 2.0) if avg_time > 0 else 0
        
        # Calculate confidence score (0.0 to 1.0)
        confidence_score = (accuracy * 0.7) + (min(time_factor, 1.0) * 0.3)
        
        # Determine mastery level
        if confidence_score >= 0.9:
            mastery_level = MasteryLevel.MASTERED
        elif confidence_score >= 0.75:
            mastery_level = MasteryLevel.STRONG
        elif confidence_score >= 0.6:
            mastery_level = MasteryLevel.AVERAGE
        elif confidence_score >= 0.3:
            mastery_level = MasteryLevel.WEAK
        else:
            mastery_level = MasteryLevel.WEAK
        
        # Update or create mastery tracking
        mastery_tracking = db.query(models.MasteryTracking).filter(
            and_(
                models.MasteryTracking.user_id == user_id,
                models.MasteryTracking.topic_id == topic_id
            )
        ).first()
        
        if not mastery_tracking:
            mastery_tracking = models.MasteryTracking(
                user_id=user_id,
                topic_id=topic_id
            )
            db.add(mastery_tracking)
        
        mastery_tracking.mastery_level = mastery_level
        mastery_tracking.confidence_score = confidence_score
        mastery_tracking.total_attempts = total_answers
        mastery_tracking.correct_attempts = correct_answers
        mastery_tracking.last_updated = datetime.utcnow()
        mastery_tracking.factors = {
            "accuracy": accuracy,
            "time_factor": time_factor,
            "avg_time_seconds": avg_time,
            "expected_time_seconds": avg_expected_time
        }
        
        db.commit()
        db.refresh(mastery_tracking)
        
        return mastery_level
    
    @staticmethod
    def update_topic_progress(db: Session, user_id: int, topic_id: int):
        """Update topic completion progress based on content blocks and checkpoints."""
        # Get topic content blocks and checkpoints
        topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
        if not topic:
            return
        
        content_blocks = db.query(models.ContentBlock).filter(
            models.ContentBlock.topic_id == topic_id
        ).count()
        
        checkpoints = db.query(models.Checkpoint).filter(
            models.Checkpoint.topic_id == topic_id
        ).all()
        
        # Count completed checkpoints (answered correctly)
        completed_checkpoints = 0
        if checkpoints:
            checkpoint_ids = [cp.id for cp in checkpoints]
            correct_answers = db.query(models.UserAnswer).filter(
                and_(
                    models.UserAnswer.user_id == user_id,
                    models.UserAnswer.checkpoint_id.in_(checkpoint_ids),
                    models.UserAnswer.is_correct == True
                )
            ).count()
            completed_checkpoints = correct_answers
        
        # Calculate completion percentage
        total_items = content_blocks + len(checkpoints)
        completed_items = content_blocks + completed_checkpoints  # Assume content blocks are "read"
        completion_percentage = (completed_items / total_items * 100) if total_items > 0 else 0
        
        # Update user progress
        progress = db.query(models.UserProgress).filter(
            and_(
                models.UserProgress.user_id == user_id,
                models.UserProgress.topic_id == topic_id
            )
        ).first()
        
        if progress:
            progress.completion_percentage = min(completion_percentage, 100.0)
            progress.is_completed = completion_percentage >= 100.0
            if progress.is_completed and not progress.completed_at:
                progress.completed_at = datetime.utcnow()
        
        db.commit()
    
    @staticmethod
    def get_user_analytics(db: Session, user_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for a user."""
        # Get all user progress
        progress_records = db.query(models.UserProgress).filter(
            models.UserProgress.user_id == user_id
        ).all()
        
        # Get mastery tracking
        mastery_records = db.query(models.MasteryTracking).filter(
            models.MasteryTracking.user_id == user_id
        ).all()
        
        # Calculate overall statistics
        total_topics = len(progress_records)
        completed_topics = len([p for p in progress_records if p.is_completed])
        total_time_minutes = sum(p.time_spent_minutes for p in progress_records)
        
        # Get weak and strong topics
        weak_topics = []
        strong_topics = []
        
        for mastery in mastery_records:
            topic = db.query(models.Topic).filter(models.Topic.id == mastery.topic_id).first()
            if topic:
                topic_data = {
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "mastery_level": mastery.mastery_level,
                    "confidence_score": mastery.confidence_score,
                    "accuracy": mastery.factors.get("accuracy", 0) if mastery.factors else 0
                }
                
                if mastery.mastery_level in [MasteryLevel.WEAK, MasteryLevel.NOT_STARTED]:
                    weak_topics.append(topic_data)
                elif mastery.mastery_level in [MasteryLevel.STRONG, MasteryLevel.MASTERED]:
                    strong_topics.append(topic_data)
        
        # Sort by confidence score
        weak_topics.sort(key=lambda x: x["confidence_score"])
        strong_topics.sort(key=lambda x: x["confidence_score"], reverse=True)
        
        return {
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "completion_percentage": (completed_topics / total_topics * 100) if total_topics > 0 else 0,
            "total_study_time_minutes": total_time_minutes,
            "weak_topics": weak_topics[:10],  # Top 10 weak topics
            "strong_topics": strong_topics[:10],  # Top 10 strong topics
            "average_confidence": sum(m.confidence_score for m in mastery_records) / len(mastery_records) if mastery_records else 0
        }
    
    @staticmethod
    def get_weekly_report(db: Session, user_id: int, week_start: datetime) -> schemas.WeeklyReportData:
        """Generate weekly report for a user."""
        week_end = week_start + timedelta(days=7)
        
        # Get session analytics for the week
        sessions = db.query(models.SessionAnalytics).filter(
            and_(
                models.SessionAnalytics.user_id == user_id,
                models.SessionAnalytics.session_start >= week_start,
                models.SessionAnalytics.session_start < week_end
            )
        ).all()
        
        total_study_time = sum(s.duration_minutes or 0 for s in sessions)
        
        # Get topics completed this week
        completed_topics = db.query(models.UserProgress).filter(
            and_(
                models.UserProgress.user_id == user_id,
                models.UserProgress.completed_at >= week_start,
                models.UserProgress.completed_at < week_end
            )
        ).count()
        
        # Get questions attempted this week
        questions_attempted = db.query(models.UserAnswer).filter(
            and_(
                models.UserAnswer.user_id == user_id,
                models.UserAnswer.answered_at >= week_start,
                models.UserAnswer.answered_at < week_end
            )
        ).count()
        
        # Calculate accuracy for the week
        correct_answers = db.query(models.UserAnswer).filter(
            and_(
                models.UserAnswer.user_id == user_id,
                models.UserAnswer.answered_at >= week_start,
                models.UserAnswer.answered_at < week_end,
                models.UserAnswer.is_correct == True
            )
        ).count()
        
        accuracy_percentage = (correct_answers / questions_attempted * 100) if questions_attempted > 0 else 0
        
        # Get current analytics to determine strong/weak topics
        analytics = AnalyticsService.get_user_analytics(db, user_id)
        
        # Generate recommendations
        recommendations = AnalyticsService._generate_recommendations(analytics, total_study_time, accuracy_percentage)
        
        return schemas.WeeklyReportData(
            week_start_date=week_start,
            week_end_date=week_end,
            total_study_time_minutes=total_study_time,
            topics_completed=completed_topics,
            questions_attempted=questions_attempted,
            accuracy_percentage=accuracy_percentage,
            strong_topics=[topic["topic_name"] for topic in analytics["strong_topics"][:5]],
            weak_topics=[topic["topic_name"] for topic in analytics["weak_topics"][:5]],
            recommendations=recommendations
        )
    
    @staticmethod
    def _generate_recommendations(analytics: Dict[str, Any], study_time: float, accuracy: float) -> List[str]:
        """Generate personalized recommendations based on analytics."""
        recommendations = []
        
        if study_time < 180:  # Less than 3 hours per week
            recommendations.append("Try to study for at least 3 hours per week for better retention.")
        
        if accuracy < 70:
            recommendations.append("Focus on understanding concepts before moving to new topics.")
            recommendations.append("Review the explanation sections for topics you're struggling with.")
        
        if len(analytics["weak_topics"]) > 5:
            recommendations.append("You have several weak topics. Focus on 2-3 topics at a time.")
        
        if analytics["weak_topics"]:
            top_weak = analytics["weak_topics"][0]
            recommendations.append(f"Priority: Review '{top_weak['topic_name']}' - your weakest topic.")
        
        if study_time > 300:  # More than 5 hours
            recommendations.append("Great study consistency! Consider taking practice tests.")
        
        if accuracy > 85:
            recommendations.append("Excellent accuracy! Try harder difficulty questions.")
        
        return recommendations[:5]  # Return top 5 recommendations