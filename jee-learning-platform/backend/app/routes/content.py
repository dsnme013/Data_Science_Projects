from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database.database import get_db
from app.models import models, schemas
from app.utils.auth import get_current_active_user, is_teacher_or_admin
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/content", tags=["content"])

# Course Routes
@router.get("/courses", response_model=List[schemas.CourseNavigation])
async def get_courses_with_navigation(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all courses with navigation structure and user progress."""
    courses = db.query(models.Course).filter(models.Course.is_active == True).all()
    
    course_navigation = []
    for course in courses:
        chapters = db.query(models.Chapter).filter(
            and_(models.Chapter.course_id == course.id, models.Chapter.is_active == True)
        ).order_by(models.Chapter.order_index).all()
        
        chapter_nav = []
        total_course_topics = 0
        completed_course_topics = 0
        
        for chapter in chapters:
            topics = db.query(models.Topic).filter(
                and_(models.Topic.chapter_id == chapter.id, models.Topic.is_active == True)
            ).order_by(models.Topic.order_index).all()
            
            topic_nav = []
            total_chapter_topics = 0
            completed_chapter_topics = 0
            
            for topic in topics:
                # Get user progress for this topic
                progress = db.query(models.UserProgress).filter(
                    and_(
                        models.UserProgress.user_id == current_user.id,
                        models.UserProgress.topic_id == topic.id
                    )
                ).first()
                
                # Get mastery tracking
                mastery = db.query(models.MasteryTracking).filter(
                    and_(
                        models.MasteryTracking.user_id == current_user.id,
                        models.MasteryTracking.topic_id == topic.id
                    )
                ).first()
                
                completion_percentage = progress.completion_percentage if progress else 0.0
                mastery_level = mastery.mastery_level if mastery else models.MasteryLevel.NOT_STARTED
                
                topic_nav.append(schemas.TopicNavigation(
                    id=topic.id,
                    name=topic.name,
                    order_index=topic.order_index,
                    completion_percentage=completion_percentage,
                    mastery_level=mastery_level,
                    estimated_time_minutes=topic.estimated_time_minutes
                ))
                
                total_chapter_topics += 1
                if completion_percentage >= 100:
                    completed_chapter_topics += 1
            
            chapter_completion = (completed_chapter_topics / total_chapter_topics * 100) if total_chapter_topics > 0 else 0
            
            chapter_nav.append(schemas.ChapterNavigation(
                id=chapter.id,
                name=chapter.name,
                order_index=chapter.order_index,
                topics=topic_nav,
                completion_percentage=chapter_completion
            ))
            
            total_course_topics += total_chapter_topics
            completed_course_topics += completed_chapter_topics
        
        course_completion = (completed_course_topics / total_course_topics * 100) if total_course_topics > 0 else 0
        
        course_navigation.append(schemas.CourseNavigation(
            id=course.id,
            name=course.name,
            code=course.code,
            chapters=chapter_nav,
            completion_percentage=course_completion
        ))
    
    return course_navigation

@router.post("/courses", response_model=schemas.Course)
async def create_course(
    course: schemas.CourseCreate,
    current_user: models.User = Depends(is_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new course (admin/teacher only)."""
    # Check if course code already exists
    existing_course = db.query(models.Course).filter(
        models.Course.code == course.code
    ).first()
    if existing_course:
        raise HTTPException(
            status_code=400,
            detail="Course code already exists"
        )
    
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

# Chapter Routes
@router.post("/chapters", response_model=schemas.Chapter)
async def create_chapter(
    chapter: schemas.ChapterCreate,
    current_user: models.User = Depends(is_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new chapter (admin/teacher only)."""
    db_chapter = models.Chapter(**chapter.dict())
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter

# Topic Routes
@router.get("/topics/{topic_id}", response_model=schemas.TopicContent)
async def get_topic_content(
    topic_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get complete topic content including blocks and checkpoints."""
    # Start session analytics
    session = AnalyticsService.start_session(db, current_user.id, topic_id)
    
    # Get topic
    topic = db.query(models.Topic).filter(
        and_(models.Topic.id == topic_id, models.Topic.is_active == True)
    ).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get content blocks
    content_blocks = db.query(models.ContentBlock).filter(
        and_(
            models.ContentBlock.topic_id == topic_id,
            models.ContentBlock.is_active == True
        )
    ).order_by(models.ContentBlock.order_index).all()
    
    # Get checkpoints (hide correct answers from students)
    checkpoints = db.query(models.Checkpoint).filter(
        and_(
            models.Checkpoint.topic_id == topic_id,
            models.Checkpoint.is_active == True
        )
    ).order_by(models.Checkpoint.order_index).all()
    
    # Convert to user-safe format (hide correct answers)
    checkpoint_for_user = []
    for checkpoint in checkpoints:
        checkpoint_for_user.append(schemas.CheckpointForUser(
            id=checkpoint.id,
            question=checkpoint.question,
            question_type=checkpoint.question_type,
            options=checkpoint.options,
            explanation=checkpoint.explanation,
            difficulty_level=checkpoint.difficulty_level,
            order_index=checkpoint.order_index,
            points=checkpoint.points,
            time_limit_seconds=checkpoint.time_limit_seconds
        ))
    
    # Get user progress
    progress = db.query(models.UserProgress).filter(
        and_(
            models.UserProgress.user_id == current_user.id,
            models.UserProgress.topic_id == topic_id
        )
    ).first()
    
    # Get mastery tracking
    mastery = db.query(models.MasteryTracking).filter(
        and_(
            models.MasteryTracking.user_id == current_user.id,
            models.MasteryTracking.topic_id == topic_id
        )
    ).first()
    
    return schemas.TopicContent(
        topic=topic,
        content_blocks=content_blocks,
        checkpoints=checkpoint_for_user,
        user_progress=progress,
        mastery_tracking=mastery
    )

@router.post("/topics", response_model=schemas.Topic)
async def create_topic(
    topic: schemas.TopicCreate,
    current_user: models.User = Depends(is_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new topic (admin/teacher only)."""
    db_topic = models.Topic(**topic.dict())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

# Content Block Routes
@router.post("/content-blocks", response_model=schemas.ContentBlock)
async def create_content_block(
    content_block: schemas.ContentBlockCreate,
    current_user: models.User = Depends(is_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new content block (admin/teacher only)."""
    db_content_block = models.ContentBlock(**content_block.dict())
    db.add(db_content_block)
    db.commit()
    db.refresh(db_content_block)
    return db_content_block

# Checkpoint Routes
@router.post("/checkpoints", response_model=schemas.Checkpoint)
async def create_checkpoint(
    checkpoint: schemas.CheckpointCreate,
    current_user: models.User = Depends(is_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new checkpoint (admin/teacher only)."""
    db_checkpoint = models.Checkpoint(**checkpoint.dict())
    db.add(db_checkpoint)
    db.commit()
    db.refresh(db_checkpoint)
    return db_checkpoint

@router.post("/checkpoints/{checkpoint_id}/answer", response_model=schemas.UserAnswer)
async def submit_checkpoint_answer(
    checkpoint_id: int,
    answer: schemas.UserAnswerCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit answer to a checkpoint."""
    # Get checkpoint
    checkpoint = db.query(models.Checkpoint).filter(
        models.Checkpoint.id == checkpoint_id
    ).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    # Check if answer is correct
    is_correct = answer.user_answer.strip().upper() == checkpoint.correct_answer.strip().upper()
    
    # Get attempt number
    existing_attempts = db.query(models.UserAnswer).filter(
        and_(
            models.UserAnswer.user_id == current_user.id,
            models.UserAnswer.checkpoint_id == checkpoint_id
        )
    ).count()
    
    # Create user answer record
    db_answer = models.UserAnswer(
        user_id=current_user.id,
        checkpoint_id=checkpoint_id,
        user_answer=answer.user_answer,
        is_correct=is_correct,
        time_taken_seconds=answer.time_taken_seconds,
        attempt_number=existing_attempts + 1
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    
    # Update mastery tracking
    AnalyticsService.calculate_mastery_level(db, current_user.id, checkpoint.topic_id)
    
    # Update topic progress
    AnalyticsService.update_topic_progress(db, current_user.id, checkpoint.topic_id)
    
    return db_answer

@router.post("/topics/{topic_id}/time-tracking")
async def track_time_on_topic(
    topic_id: int,
    time_spent_minutes: float,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Track time spent on a topic."""
    progress = AnalyticsService.track_time_on_topic(
        db, current_user.id, topic_id, time_spent_minutes
    )
    return {"message": "Time tracked successfully", "total_time": progress.time_spent_minutes}

@router.post("/sessions/{session_id}/end")
async def end_study_session(
    session_id: int,
    session_data: schemas.SessionEnd,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """End a study session."""
    AnalyticsService.end_session(db, session_id, session_data.actions_taken)
    return {"message": "Session ended successfully"}