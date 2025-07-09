from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum
from datetime import datetime

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, enum.Enum):
    MCQ = "mcq"
    NUMERICAL = "numerical"
    SUBJECTIVE = "subjective"

class MasteryLevel(str, enum.Enum):
    NOT_STARTED = "not_started"
    WEAK = "weak"
    AVERAGE = "average"
    STRONG = "strong"
    MASTERED = "mastered"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # JEE specific fields
    target_exam_year = Column(Integer)
    preferred_language = Column(String, default="english")
    current_class = Column(String)
    
    # Relationships
    user_progress = relationship("UserProgress", back_populates="user")
    session_analytics = relationship("SessionAnalytics", back_populates="user")
    user_answers = relationship("UserAnswer", back_populates="user")
    mastery_tracking = relationship("MasteryTracking", back_populates="user")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Math, Physics, Chemistry
    description = Column(Text)
    code = Column(String, unique=True, nullable=False)  # MATH_JEE, PHYS_JEE, CHEM_JEE
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chapters = relationship("Chapter", back_populates="course")

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    order_index = Column(Integer, nullable=False)
    estimated_hours = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="chapters")
    topics = relationship("Topic", back_populates="chapter")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    order_index = Column(Integer, nullable=False)
    estimated_time_minutes = Column(Integer)
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    prerequisites = Column(JSON)  # List of topic IDs that should be completed first
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chapter = relationship("Chapter", back_populates="topics")
    content_blocks = relationship("ContentBlock", back_populates="topic")
    checkpoints = relationship("Checkpoint", back_populates="topic")

class ContentBlock(Base):
    __tablename__ = "content_blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Markdown content
    content_type = Column(String, default="explanation")  # explanation, example, formula, etc.
    order_index = Column(Integer, nullable=False)
    media_urls = Column(JSON)  # Images, videos, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="content_blocks")

class Checkpoint(Base):
    __tablename__ = "checkpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    question = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), default=QuestionType.MCQ)
    options = Column(JSON)  # For MCQ: ["option1", "option2", "option3", "option4"]
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    order_index = Column(Integer, nullable=False)
    points = Column(Integer, default=1)
    time_limit_seconds = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="checkpoints")
    user_answers = relationship("UserAnswer", back_populates="checkpoint")

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    time_spent_minutes = Column(Float, default=0.0)
    last_accessed = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="user_progress")
    topic = relationship("Topic")

class SessionAnalytics(Base):
    __tablename__ = "session_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    session_start = Column(DateTime(timezone=True), server_default=func.now())
    session_end = Column(DateTime(timezone=True))
    duration_minutes = Column(Float)
    actions_taken = Column(JSON)  # Track user interactions
    device_info = Column(JSON)
    ip_address = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="session_analytics")
    topic = relationship("Topic")

class UserAnswer(Base):
    __tablename__ = "user_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checkpoint_id = Column(Integer, ForeignKey("checkpoints.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Float)
    attempt_number = Column(Integer, default=1)
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_answers")
    checkpoint = relationship("Checkpoint", back_populates="user_answers")

class MasteryTracking(Base):
    __tablename__ = "mastery_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    mastery_level = Column(Enum(MasteryLevel), default=MasteryLevel.NOT_STARTED)
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    factors = Column(JSON)  # Speed, accuracy, consistency metrics
    
    # Relationships
    user = relationship("User", back_populates="mastery_tracking")
    topic = relationship("Topic")

class AdaptiveQuiz(Base):
    __tablename__ = "adaptive_quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_questions = Column(JSON)  # AI generated questions
    quiz_type = Column(String)  # weakness_focus, speed_practice, comprehensive_review
    target_topics = Column(JSON)  # Topic IDs this quiz targets
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    score = Column(Float)
    time_taken_minutes = Column(Float)
    
    # Relationships
    user = relationship("User")

class WeeklyReport(Base):
    __tablename__ = "weekly_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start_date = Column(DateTime(timezone=True), nullable=False)
    week_end_date = Column(DateTime(timezone=True), nullable=False)
    total_study_time_minutes = Column(Float, default=0.0)
    topics_completed = Column(Integer, default=0)
    questions_attempted = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)
    strong_topics = Column(JSON)
    weak_topics = Column(JSON)
    recommendations = Column(JSON)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")