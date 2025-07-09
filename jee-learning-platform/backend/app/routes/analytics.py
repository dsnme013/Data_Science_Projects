from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import models, schemas
from app.utils.auth import get_current_active_user, is_teacher_or_admin
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_user_dashboard(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive dashboard analytics for the current user."""
    analytics = AnalyticsService.get_user_analytics(db, current_user.id)
    
    # Get recent study sessions
    recent_sessions = db.query(models.SessionAnalytics).filter(
        models.SessionAnalytics.user_id == current_user.id
    ).order_by(models.SessionAnalytics.session_start.desc()).limit(10).all()
    
    # Get weekly progress
    week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    weekly_report = AnalyticsService.get_weekly_report(db, current_user.id, week_start)
    
    return {
        "user_analytics": analytics,
        "recent_sessions": [
            {
                "id": session.id,
                "topic_id": session.topic_id,
                "duration_minutes": session.duration_minutes,
                "session_start": session.session_start,
                "session_end": session.session_end
            } for session in recent_sessions
        ],
        "weekly_report": weekly_report,
        "study_streak": calculate_study_streak(db, current_user.id),
        "next_recommendations": get_next_study_recommendations(analytics)
    }

@router.get("/progress")
async def get_user_progress(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[schemas.UserProgress]:
    """Get detailed progress for all topics."""
    return db.query(models.UserProgress).filter(
        models.UserProgress.user_id == current_user.id
    ).all()

@router.get("/mastery")
async def get_mastery_tracking(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[schemas.MasteryTracking]:
    """Get mastery tracking for all topics."""
    return db.query(models.MasteryTracking).filter(
        models.MasteryTracking.user_id == current_user.id
    ).order_by(models.MasteryTracking.confidence_score).all()

@router.get("/weekly-report")
async def get_weekly_report(
    week_start: datetime = Query(..., description="Start date of the week"),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> schemas.WeeklyReportData:
    """Get weekly report for a specific week."""
    return AnalyticsService.get_weekly_report(db, current_user.id, week_start)

@router.get("/topic-analytics/{topic_id}")
async def get_topic_analytics(
    topic_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed analytics for a specific topic."""
    # Get topic information
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get user progress
    progress = db.query(models.UserProgress).filter(
        models.UserProgress.user_id == current_user.id,
        models.UserProgress.topic_id == topic_id
    ).first()
    
    # Get mastery tracking
    mastery = db.query(models.MasteryTracking).filter(
        models.MasteryTracking.user_id == current_user.id,
        models.MasteryTracking.topic_id == topic_id
    ).first()
    
    # Get user answers for topic checkpoints
    checkpoints = db.query(models.Checkpoint).filter(
        models.Checkpoint.topic_id == topic_id
    ).all()
    checkpoint_ids = [cp.id for cp in checkpoints]
    
    user_answers = db.query(models.UserAnswer).filter(
        models.UserAnswer.user_id == current_user.id,
        models.UserAnswer.checkpoint_id.in_(checkpoint_ids)
    ).all()
    
    # Calculate statistics
    correct_answers = [ans for ans in user_answers if ans.is_correct]
    accuracy = len(correct_answers) / len(user_answers) * 100 if user_answers else 0
    avg_time = sum(ans.time_taken_seconds or 0 for ans in user_answers) / len(user_answers) if user_answers else 0
    
    return {
        "topic": {
            "id": topic.id,
            "name": topic.name,
            "description": topic.description,
            "difficulty_level": topic.difficulty_level,
            "estimated_time_minutes": topic.estimated_time_minutes
        },
        "progress": progress,
        "mastery": mastery,
        "performance": {
            "total_attempts": len(user_answers),
            "correct_attempts": len(correct_answers),
            "accuracy_percentage": accuracy,
            "average_time_seconds": avg_time
        },
        "answer_history": [
            {
                "checkpoint_id": ans.checkpoint_id,
                "is_correct": ans.is_correct,
                "time_taken_seconds": ans.time_taken_seconds,
                "answered_at": ans.answered_at,
                "attempt_number": ans.attempt_number
            } for ans in user_answers
        ]
    }

@router.get("/course-analytics/{course_id}")
async def get_course_analytics(
    course_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> schemas.CourseAnalytics:
    """Get comprehensive analytics for a course."""
    # Get course
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Get all topics in the course
    topics = db.query(models.Topic).join(models.Chapter).filter(
        models.Chapter.course_id == course_id
    ).all()
    
    topic_analytics = []
    total_topics = len(topics)
    completed_topics = 0
    total_time = 0
    total_correct = 0
    total_attempts = 0
    
    for topic in topics:
        # Get progress
        progress = db.query(models.UserProgress).filter(
            models.UserProgress.user_id == current_user.id,
            models.UserProgress.topic_id == topic.id
        ).first()
        
        # Get mastery
        mastery = db.query(models.MasteryTracking).filter(
            models.MasteryTracking.user_id == current_user.id,
            models.MasteryTracking.topic_id == topic.id
        ).first()
        
        completion_percentage = progress.completion_percentage if progress else 0
        time_spent = progress.time_spent_minutes if progress else 0
        mastery_level = mastery.mastery_level if mastery else models.MasteryLevel.NOT_STARTED
        
        if completion_percentage >= 100:
            completed_topics += 1
        
        total_time += time_spent
        
        if mastery:
            total_correct += mastery.correct_attempts
            total_attempts += mastery.total_attempts
        
        topic_data = schemas.TopicAnalytics(
            topic_id=topic.id,
            topic_name=topic.name,
            time_spent_minutes=time_spent,
            completion_percentage=completion_percentage,
            mastery_level=mastery_level,
            accuracy_percentage=mastery.factors.get("accuracy", 0) * 100 if mastery and mastery.factors else 0,
            last_accessed=progress.last_accessed if progress else None
        )
        topic_analytics.append(topic_data)
    
    # Separate weak and strong topics
    weak_topics = [t for t in topic_analytics if t.mastery_level in [models.MasteryLevel.WEAK, models.MasteryLevel.NOT_STARTED]]
    strong_topics = [t for t in topic_analytics if t.mastery_level in [models.MasteryLevel.STRONG, models.MasteryLevel.MASTERED]]
    
    # Sort by accuracy/confidence
    weak_topics.sort(key=lambda x: x.accuracy_percentage)
    strong_topics.sort(key=lambda x: x.accuracy_percentage, reverse=True)
    
    average_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
    
    return schemas.CourseAnalytics(
        course_id=course.id,
        course_name=course.name,
        total_topics=total_topics,
        completed_topics=completed_topics,
        total_time_minutes=total_time,
        average_accuracy=average_accuracy,
        weak_topics=weak_topics[:10],
        strong_topics=strong_topics[:10]
    )

@router.get("/study-pattern")
async def get_study_pattern(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get study pattern analysis for the user."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get session data
    sessions = db.query(models.SessionAnalytics).filter(
        models.SessionAnalytics.user_id == current_user.id,
        models.SessionAnalytics.session_start >= start_date
    ).all()
    
    # Analyze daily patterns
    daily_study_time = {}
    hourly_distribution = [0] * 24
    
    for session in sessions:
        if session.duration_minutes:
            date_str = session.session_start.date().isoformat()
            daily_study_time[date_str] = daily_study_time.get(date_str, 0) + session.duration_minutes
            
            hour = session.session_start.hour
            hourly_distribution[hour] += session.duration_minutes
    
    # Calculate streaks and consistency
    study_streak = calculate_study_streak(db, current_user.id)
    avg_daily_time = sum(daily_study_time.values()) / len(daily_study_time) if daily_study_time else 0
    
    return {
        "daily_study_time": daily_study_time,
        "hourly_distribution": hourly_distribution,
        "current_streak_days": study_streak,
        "average_daily_minutes": avg_daily_time,
        "total_sessions": len(sessions),
        "total_study_time_minutes": sum(s.duration_minutes or 0 for s in sessions),
        "most_productive_hour": hourly_distribution.index(max(hourly_distribution)) if any(hourly_distribution) else None
    }

# Admin/Teacher routes
@router.get("/admin/users/{user_id}/analytics")
async def get_user_analytics_admin(
    user_id: int,
    current_user: models.User = Depends(is_teacher_or_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get analytics for any user (admin/teacher only)."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    analytics = AnalyticsService.get_user_analytics(db, user_id)
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email
        },
        "analytics": analytics
    }

@router.get("/admin/course-stats/{course_id}")
async def get_course_statistics(
    course_id: int,
    current_user: models.User = Depends(is_teacher_or_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get course-wide statistics (admin/teacher only)."""
    # Get all users who have progress in this course
    course_topics = db.query(models.Topic).join(models.Chapter).filter(
        models.Chapter.course_id == course_id
    ).all()
    topic_ids = [t.id for t in course_topics]
    
    # Get all progress records for these topics
    progress_records = db.query(models.UserProgress).filter(
        models.UserProgress.topic_id.in_(topic_ids)
    ).all()
    
    # Calculate statistics
    unique_users = set(p.user_id for p in progress_records)
    total_users = len(unique_users)
    
    completed_topics_per_user = {}
    for progress in progress_records:
        if progress.is_completed:
            completed_topics_per_user[progress.user_id] = completed_topics_per_user.get(progress.user_id, 0) + 1
    
    avg_completion_rate = sum(completed_topics_per_user.values()) / total_users if total_users > 0 else 0
    
    return {
        "course_id": course_id,
        "total_enrolled_users": total_users,
        "total_topics": len(course_topics),
        "average_topics_completed": avg_completion_rate,
        "completion_distribution": completed_topics_per_user
    }

def calculate_study_streak(db: Session, user_id: int) -> int:
    """Calculate current study streak in days."""
    sessions = db.query(models.SessionAnalytics).filter(
        models.SessionAnalytics.user_id == user_id
    ).order_by(models.SessionAnalytics.session_start.desc()).all()
    
    if not sessions:
        return 0
    
    streak = 0
    current_date = datetime.utcnow().date()
    
    # Group sessions by date
    sessions_by_date = {}
    for session in sessions:
        date = session.session_start.date()
        if date not in sessions_by_date:
            sessions_by_date[date] = []
        sessions_by_date[date].append(session)
    
    # Count consecutive days
    while current_date in sessions_by_date:
        streak += 1
        current_date -= timedelta(days=1)
    
    return streak

def get_next_study_recommendations(analytics: Dict[str, Any]) -> List[str]:
    """Generate next study recommendations based on analytics."""
    recommendations = []
    
    if analytics["weak_topics"]:
        top_weak = analytics["weak_topics"][0]
        recommendations.append(f"Focus on: {top_weak['topic_name']} (Confidence: {top_weak['confidence_score']:.0%})")
    
    if analytics["completion_percentage"] < 50:
        recommendations.append("Continue with your current learning path")
    elif analytics["completion_percentage"] > 80:
        recommendations.append("Great progress! Consider taking practice tests")
    
    if analytics["average_confidence"] > 0.7:
        recommendations.append("You're doing well! Try some challenging practice problems")
    
    return recommendations[:3]