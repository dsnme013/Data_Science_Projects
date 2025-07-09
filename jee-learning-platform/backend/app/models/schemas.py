from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.models import UserRole, DifficultyLevel, QuestionType, MasteryLevel

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    target_exam_year: Optional[int] = None
    preferred_language: str = "english"
    current_class: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    target_exam_year: Optional[int] = None
    preferred_language: Optional[str] = None
    current_class: Optional[str] = None

class User(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Course Schemas
class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    code: str

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chapter Schemas
class ChapterBase(BaseModel):
    course_id: int
    name: str
    description: Optional[str] = None
    order_index: int
    estimated_hours: Optional[float] = None

class ChapterCreate(ChapterBase):
    pass

class Chapter(ChapterBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Topic Schemas
class TopicBase(BaseModel):
    chapter_id: int
    name: str
    description: Optional[str] = None
    order_index: int
    estimated_time_minutes: Optional[int] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    prerequisites: Optional[List[int]] = None

class TopicCreate(TopicBase):
    pass

class Topic(TopicBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TopicWithProgress(Topic):
    completion_percentage: float = 0.0
    mastery_level: MasteryLevel = MasteryLevel.NOT_STARTED
    time_spent_minutes: float = 0.0

# Content Block Schemas
class ContentBlockBase(BaseModel):
    topic_id: int
    title: str
    content: str
    content_type: str = "explanation"
    order_index: int
    media_urls: Optional[List[str]] = None

class ContentBlockCreate(ContentBlockBase):
    pass

class ContentBlock(ContentBlockBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Checkpoint Schemas
class CheckpointBase(BaseModel):
    topic_id: int
    question: str
    question_type: QuestionType = QuestionType.MCQ
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    order_index: int
    points: int = 1
    time_limit_seconds: int = 60

class CheckpointCreate(CheckpointBase):
    pass

class Checkpoint(CheckpointBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CheckpointForUser(BaseModel):
    id: int
    question: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    difficulty_level: DifficultyLevel
    order_index: int
    points: int
    time_limit_seconds: int
    
    class Config:
        from_attributes = True

# User Answer Schemas
class UserAnswerBase(BaseModel):
    checkpoint_id: int
    user_answer: str
    time_taken_seconds: Optional[float] = None

class UserAnswerCreate(UserAnswerBase):
    pass

class UserAnswer(UserAnswerBase):
    id: int
    user_id: int
    is_correct: bool
    attempt_number: int
    answered_at: datetime
    
    class Config:
        from_attributes = True

# Progress Schemas
class UserProgressBase(BaseModel):
    topic_id: int
    completion_percentage: float = 0.0
    time_spent_minutes: float = 0.0

class UserProgressCreate(UserProgressBase):
    pass

class UserProgress(UserProgressBase):
    id: int
    user_id: int
    is_completed: bool
    last_accessed: Optional[datetime] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Session Analytics Schemas
class SessionStart(BaseModel):
    topic_id: Optional[int] = None
    device_info: Optional[Dict[str, Any]] = None

class SessionEnd(BaseModel):
    session_id: int
    actions_taken: Optional[List[Dict[str, Any]]] = None

class SessionAnalytics(BaseModel):
    id: int
    user_id: int
    topic_id: Optional[int] = None
    session_start: datetime
    session_end: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    actions_taken: Optional[List[Dict[str, Any]]] = None
    device_info: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Mastery Tracking Schemas
class MasteryTrackingBase(BaseModel):
    topic_id: int
    mastery_level: MasteryLevel
    confidence_score: float = 0.0

class MasteryTracking(MasteryTrackingBase):
    id: int
    user_id: int
    total_attempts: int
    correct_attempts: int
    last_updated: datetime
    factors: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Analytics Schemas
class TopicAnalytics(BaseModel):
    topic_id: int
    topic_name: str
    time_spent_minutes: float
    completion_percentage: float
    mastery_level: MasteryLevel
    accuracy_percentage: float
    last_accessed: Optional[datetime] = None

class CourseAnalytics(BaseModel):
    course_id: int
    course_name: str
    total_topics: int
    completed_topics: int
    total_time_minutes: float
    average_accuracy: float
    weak_topics: List[TopicAnalytics]
    strong_topics: List[TopicAnalytics]

class WeeklyReportData(BaseModel):
    week_start_date: datetime
    week_end_date: datetime
    total_study_time_minutes: float
    topics_completed: int
    questions_attempted: int
    accuracy_percentage: float
    strong_topics: List[str]
    weak_topics: List[str]
    recommendations: List[str]

# Adaptive Quiz Schemas
class AdaptiveQuizRequest(BaseModel):
    quiz_type: str  # weakness_focus, speed_practice, comprehensive_review
    target_topics: Optional[List[int]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    num_questions: int = 10

class GeneratedQuestion(BaseModel):
    question: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    difficulty_level: DifficultyLevel
    topic_id: int

class AdaptiveQuiz(BaseModel):
    id: int
    quiz_type: str
    target_topics: List[int]
    generated_questions: List[GeneratedQuestion]
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuizSubmission(BaseModel):
    quiz_id: int
    answers: List[Dict[str, Any]]  # [{question_index: 0, user_answer: "A", time_taken: 45.2}]

# Navigation Schemas
class TopicNavigation(BaseModel):
    id: int
    name: str
    order_index: int
    completion_percentage: float
    mastery_level: MasteryLevel
    estimated_time_minutes: Optional[int] = None

class ChapterNavigation(BaseModel):
    id: int
    name: str
    order_index: int
    topics: List[TopicNavigation]
    completion_percentage: float

class CourseNavigation(BaseModel):
    id: int
    name: str
    code: str
    chapters: List[ChapterNavigation]
    completion_percentage: float

# Content Display Schemas
class TopicContent(BaseModel):
    topic: Topic
    content_blocks: List[ContentBlock]
    checkpoints: List[CheckpointForUser]
    user_progress: Optional[UserProgress] = None
    mastery_tracking: Optional[MasteryTracking] = None

# Learning Path Schemas
class LearningPathItem(BaseModel):
    topic_id: int
    topic_name: str
    reason: str
    priority: int
    estimated_time_minutes: int

class PersonalizedLearningPath(BaseModel):
    user_id: int
    generated_at: datetime
    recommended_topics: List[LearningPathItem]
    study_plan: Dict[str, Any]
    tips: List[str]