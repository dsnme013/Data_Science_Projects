from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import models, schemas
from app.utils.auth import get_current_active_user
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/ai", tags=["ai"])
ai_service = AIService()

@router.post("/generate-quiz", response_model=schemas.AdaptiveQuiz)
async def generate_adaptive_quiz(
    quiz_request: schemas.AdaptiveQuizRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate an adaptive quiz based on user's weak areas and preferences."""
    
    # Generate questions using AI service
    generated_questions = ai_service.generate_adaptive_quiz(db, current_user.id, quiz_request)
    
    if not generated_questions:
        raise HTTPException(
            status_code=400,
            detail="Unable to generate quiz. Please ensure you have some progress data or specify target topics."
        )
    
    # Store the quiz in database for tracking
    db_quiz = models.AdaptiveQuiz(
        user_id=current_user.id,
        generated_questions=[q.dict() for q in generated_questions],
        quiz_type=quiz_request.quiz_type,
        target_topics=quiz_request.target_topics or []
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    return schemas.AdaptiveQuiz(
        id=db_quiz.id,
        quiz_type=db_quiz.quiz_type,
        target_topics=db_quiz.target_topics,
        generated_questions=generated_questions,
        created_at=db_quiz.created_at
    )

@router.post("/submit-quiz/{quiz_id}")
async def submit_quiz(
    quiz_id: int,
    submission: schemas.QuizSubmission,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit answers for an adaptive quiz."""
    
    # Get the quiz
    quiz = db.query(models.AdaptiveQuiz).filter(
        models.AdaptiveQuiz.id == quiz_id,
        models.AdaptiveQuiz.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz.completed_at:
        raise HTTPException(status_code=400, detail="Quiz already submitted")
    
    # Process answers
    total_questions = len(quiz.generated_questions)
    correct_answers = 0
    total_time = 0
    
    for answer_data in submission.answers:
        question_index = answer_data["question_index"]
        user_answer = answer_data["user_answer"]
        time_taken = answer_data.get("time_taken", 0)
        
        if 0 <= question_index < total_questions:
            question = quiz.generated_questions[question_index]
            is_correct = user_answer.strip().upper() == question["correct_answer"].strip().upper()
            
            if is_correct:
                correct_answers += 1
            
            total_time += time_taken
            
            # Create checkpoint-like tracking for quiz questions
            # This helps in mastery calculation
            topic_id = question.get("topic_id")
            if topic_id:
                # Create a temporary checkpoint record for analytics
                quiz_answer = models.UserAnswer(
                    user_id=current_user.id,
                    checkpoint_id=None,  # No actual checkpoint for quiz questions
                    user_answer=user_answer,
                    is_correct=is_correct,
                    time_taken_seconds=time_taken
                )
                # Note: We could extend this to create virtual checkpoints for quiz questions
    
    # Calculate score
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Update quiz record
    quiz.completed_at = models.func.now()
    quiz.score = score
    quiz.time_taken_minutes = total_time / 60
    
    db.commit()
    
    # Update mastery tracking for target topics based on performance
    for topic_id in quiz.target_topics:
        AnalyticsService.calculate_mastery_level(db, current_user.id, topic_id)
    
    return {
        "quiz_id": quiz_id,
        "score": score,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "time_taken_minutes": total_time / 60,
        "performance_feedback": generate_performance_feedback(score, correct_answers, total_questions)
    }

@router.get("/learning-path", response_model=schemas.PersonalizedLearningPath)
async def get_personalized_learning_path(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a personalized learning path based on user's progress and weak areas."""
    
    learning_path = ai_service.generate_learning_path(db, current_user.id)
    return learning_path

@router.get("/recommendations")
async def get_study_recommendations(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered study recommendations."""
    
    # Get user analytics
    analytics = AnalyticsService.get_user_analytics(db, current_user.id)
    
    recommendations = {
        "immediate_focus": [],
        "study_tips": [],
        "practice_suggestions": [],
        "time_management": []
    }
    
    # Generate immediate focus recommendations
    if analytics["weak_topics"]:
        top_weak_topics = analytics["weak_topics"][:3]
        for topic in top_weak_topics:
            recommendations["immediate_focus"].append({
                "topic_name": topic["topic_name"],
                "reason": f"Low confidence ({topic['confidence_score']:.1%})",
                "action": "Review concepts and practice problems"
            })
    
    # Study tips based on performance
    if analytics["average_confidence"] < 0.5:
        recommendations["study_tips"].extend([
            "Focus on understanding core concepts before attempting problems",
            "Use spaced repetition to improve retention",
            "Try explaining concepts in your own words"
        ])
    elif analytics["average_confidence"] > 0.8:
        recommendations["study_tips"].extend([
            "Challenge yourself with harder problems",
            "Try teaching concepts to others",
            "Focus on speed and accuracy in problem solving"
        ])
    
    # Practice suggestions
    if len(analytics["weak_topics"]) > 5:
        recommendations["practice_suggestions"].append("Take targeted quizzes for your weak topics")
    
    if analytics["completion_percentage"] > 70:
        recommendations["practice_suggestions"].append("Take comprehensive practice tests")
    
    # Time management
    avg_study_time = analytics.get("total_study_time_minutes", 0) / 7  # Weekly average
    if avg_study_time < 180:  # Less than 3 hours per week
        recommendations["time_management"].append("Try to study at least 30 minutes daily")
    elif avg_study_time > 420:  # More than 7 hours per week
        recommendations["time_management"].append("Great consistency! Make sure to take breaks")
    
    return recommendations

@router.post("/quiz-types/weakness-focus")
async def generate_weakness_focused_quiz(
    num_questions: int = 10,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a quiz focused on user's weakest topics."""
    
    quiz_request = schemas.AdaptiveQuizRequest(
        quiz_type="weakness_focus",
        num_questions=num_questions
    )
    
    return await generate_adaptive_quiz(quiz_request, current_user, db)

@router.post("/quiz-types/speed-practice")
async def generate_speed_practice_quiz(
    num_questions: int = 15,
    target_topics: List[int] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a quiz for speed practice with time pressure."""
    
    quiz_request = schemas.AdaptiveQuizRequest(
        quiz_type="speed_practice",
        target_topics=target_topics,
        num_questions=num_questions
    )
    
    return await generate_adaptive_quiz(quiz_request, current_user, db)

@router.post("/quiz-types/comprehensive-review")
async def generate_comprehensive_quiz(
    num_questions: int = 20,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a comprehensive review quiz covering multiple topics."""
    
    quiz_request = schemas.AdaptiveQuizRequest(
        quiz_type="comprehensive_review",
        num_questions=num_questions
    )
    
    return await generate_adaptive_quiz(quiz_request, current_user, db)

@router.get("/quiz-history")
async def get_quiz_history(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's quiz history with performance metrics."""
    
    quizzes = db.query(models.AdaptiveQuiz).filter(
        models.AdaptiveQuiz.user_id == current_user.id
    ).order_by(models.AdaptiveQuiz.created_at.desc()).limit(20).all()
    
    quiz_history = []
    for quiz in quizzes:
        quiz_data = {
            "id": quiz.id,
            "quiz_type": quiz.quiz_type,
            "created_at": quiz.created_at,
            "completed_at": quiz.completed_at,
            "score": quiz.score,
            "time_taken_minutes": quiz.time_taken_minutes,
            "num_questions": len(quiz.generated_questions) if quiz.generated_questions else 0,
            "target_topics": quiz.target_topics
        }
        quiz_history.append(quiz_data)
    
    return {
        "quiz_history": quiz_history,
        "total_quizzes": len(quiz_history),
        "average_score": sum(q["score"] or 0 for q in quiz_history) / len(quiz_history) if quiz_history else 0
    }

@router.post("/study-plan/generate")
async def generate_study_plan(
    days: int = 7,
    daily_minutes: int = 60,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a detailed study plan for the specified duration."""
    
    # Get user analytics
    analytics = AnalyticsService.get_user_analytics(db, current_user.id)
    
    # Get weak topics for prioritization
    weak_topics = analytics["weak_topics"][:10]
    
    # Generate daily study plan
    daily_plan = []
    topics_per_day = max(1, len(weak_topics) // days)
    
    for day in range(1, days + 1):
        start_idx = (day - 1) * topics_per_day
        end_idx = min(start_idx + topics_per_day, len(weak_topics))
        day_topics = weak_topics[start_idx:end_idx]
        
        daily_activities = []
        time_per_topic = daily_minutes // max(1, len(day_topics))
        
        for topic in day_topics:
            daily_activities.append({
                "topic_name": topic["topic_name"],
                "activity": "Review concepts and practice problems",
                "estimated_minutes": time_per_topic,
                "priority": "high" if topic["confidence_score"] < 0.3 else "medium"
            })
        
        daily_plan.append({
            "day": day,
            "total_minutes": daily_minutes,
            "activities": daily_activities,
            "break_reminder": "Take a 5-10 minute break between topics"
        })
    
    return {
        "study_plan": daily_plan,
        "total_days": days,
        "daily_target_minutes": daily_minutes,
        "focus_areas": [topic["topic_name"] for topic in weak_topics[:5]],
        "tips": [
            "Start with your weakest topics when you're most alert",
            "Review previous day's topics briefly before starting new ones",
            "Track your progress and adjust the plan as needed"
        ]
    }

def generate_performance_feedback(score: float, correct: int, total: int) -> dict:
    """Generate performance feedback based on quiz results."""
    
    feedback = {
        "overall": "",
        "strengths": [],
        "improvements": [],
        "next_steps": []
    }
    
    if score >= 90:
        feedback["overall"] = "Excellent performance! You have strong understanding of these topics."
        feedback["next_steps"].append("Try more challenging problems or comprehensive tests")
    elif score >= 75:
        feedback["overall"] = "Good performance! You're on the right track."
        feedback["next_steps"].append("Review the topics you missed and practice similar problems")
    elif score >= 60:
        feedback["overall"] = "Satisfactory performance with room for improvement."
        feedback["improvements"].append("Focus on understanding core concepts better")
        feedback["next_steps"].append("Spend more time on fundamentals before attempting quizzes")
    else:
        feedback["overall"] = "This topic needs more attention and practice."
        feedback["improvements"].extend([
            "Review the explanations for questions you missed",
            "Go back to the concept explanations in the learning material"
        ])
        feedback["next_steps"].append("Focus on building foundation knowledge first")
    
    accuracy_percent = (correct / total) * 100 if total > 0 else 0
    feedback["accuracy"] = f"{accuracy_percent:.1f}% ({correct}/{total})"
    
    return feedback