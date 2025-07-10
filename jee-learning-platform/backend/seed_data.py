#!/usr/bin/env python3
"""
Database seeding script for JEE Learning Platform
Populates the database with sample courses, chapters, topics, and content
"""

import json
import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine
from app.models import models
from app.models.models import DifficultyLevel, QuestionType

def load_json_content(file_path: str) -> dict:
    """Load content from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_sample_users(db: Session):
    """Create sample users for testing."""
    from app.utils.auth import get_password_hash
    
    users_data = [
        {
            "email": "student@jee.com",
            "username": "student1",
            "full_name": "Test Student",
            "password": "password123",
            "role": models.UserRole.STUDENT,
            "target_exam_year": 2024,
            "current_class": "12th"
        },
        {
            "email": "teacher@jee.com", 
            "username": "teacher1",
            "full_name": "Test Teacher",
            "password": "password123",
            "role": models.UserRole.TEACHER
        },
        {
            "email": "admin@jee.com",
            "username": "admin1", 
            "full_name": "Test Admin",
            "password": "password123",
            "role": models.UserRole.ADMIN
        }
    ]
    
    for user_data in users_data:
        # Check if user already exists
        existing_user = db.query(models.User).filter(
            models.User.email == user_data["email"]
        ).first()
        
        if not existing_user:
            user = models.User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                target_exam_year=user_data.get("target_exam_year"),
                current_class=user_data.get("current_class")
            )
            db.add(user)
            print(f"Created user: {user_data['username']}")
    
    db.commit()

def create_courses(db: Session):
    """Create the main JEE courses."""
    courses_data = [
        {
            "name": "Mathematics",
            "code": "MATH_JEE",
            "description": "Complete Mathematics curriculum for JEE Main preparation covering algebra, calculus, geometry, and more."
        },
        {
            "name": "Physics", 
            "code": "PHYS_JEE",
            "description": "Comprehensive Physics syllabus for JEE Main including mechanics, thermodynamics, electromagnetism, and modern physics."
        },
        {
            "name": "Chemistry",
            "code": "CHEM_JEE", 
            "description": "Complete Chemistry coverage for JEE Main with physical, organic, and inorganic chemistry topics."
        }
    ]
    
    created_courses = {}
    for course_data in courses_data:
        # Check if course already exists
        existing_course = db.query(models.Course).filter(
            models.Course.code == course_data["code"]
        ).first()
        
        if not existing_course:
            course = models.Course(**course_data)
            db.add(course)
            db.flush()  # Get the ID
            created_courses[course_data["code"]] = course
            print(f"Created course: {course_data['name']}")
        else:
            created_courses[course_data["code"]] = existing_course
            print(f"Course already exists: {course_data['name']}")
    
    db.commit()
    return created_courses

def seed_content_from_json(db: Session, json_file_path: str, course_id: int):
    """Seed content from a JSON file."""
    content_data = load_json_content(json_file_path)
    
    # Create chapter
    chapter_data = {
        "course_id": course_id,
        "name": content_data["chapter"],
        "description": content_data["chapter_description"],
        "order_index": content_data["order_index"],
        "estimated_hours": content_data["estimated_hours"]
    }
    
    # Check if chapter already exists
    existing_chapter = db.query(models.Chapter).filter(
        models.Chapter.course_id == course_id,
        models.Chapter.name == chapter_data["name"]
    ).first()
    
    if existing_chapter:
        chapter = existing_chapter
        print(f"Chapter already exists: {chapter_data['name']}")
    else:
        chapter = models.Chapter(**chapter_data)
        db.add(chapter)
        db.flush()
        print(f"Created chapter: {chapter_data['name']}")
    
    # Create topics
    for topic_data in content_data["topics"]:
        # Check if topic already exists
        existing_topic = db.query(models.Topic).filter(
            models.Topic.chapter_id == chapter.id,
            models.Topic.name == topic_data["name"]
        ).first()
        
        if existing_topic:
            topic = existing_topic
            print(f"  Topic already exists: {topic_data['name']}")
        else:
            topic = models.Topic(
                chapter_id=chapter.id,
                name=topic_data["name"],
                description=topic_data["description"],
                order_index=topic_data["order_index"],
                estimated_time_minutes=topic_data["estimated_time_minutes"],
                difficulty_level=getattr(DifficultyLevel, topic_data["difficulty_level"].upper()),
                prerequisites=topic_data.get("prerequisites", [])
            )
            db.add(topic)
            db.flush()
            print(f"  Created topic: {topic_data['name']}")
        
        # Create content blocks
        for content_block_data in topic_data["content_blocks"]:
            # Check if content block already exists
            existing_content = db.query(models.ContentBlock).filter(
                models.ContentBlock.topic_id == topic.id,
                models.ContentBlock.title == content_block_data["title"]
            ).first()
            
            if not existing_content:
                content_block = models.ContentBlock(
                    topic_id=topic.id,
                    title=content_block_data["title"],
                    content=content_block_data["content"],
                    content_type=content_block_data["content_type"],
                    order_index=content_block_data["order_index"],
                    media_urls=content_block_data.get("media_urls", [])
                )
                db.add(content_block)
                print(f"    Created content block: {content_block_data['title']}")
        
        # Create checkpoints
        for checkpoint_data in topic_data["checkpoints"]:
            # Check if checkpoint already exists
            existing_checkpoint = db.query(models.Checkpoint).filter(
                models.Checkpoint.topic_id == topic.id,
                models.Checkpoint.question == checkpoint_data["question"]
            ).first()
            
            if not existing_checkpoint:
                checkpoint = models.Checkpoint(
                    topic_id=topic.id,
                    question=checkpoint_data["question"],
                    question_type=getattr(QuestionType, checkpoint_data["question_type"].upper()),
                    options=checkpoint_data.get("options", []),
                    correct_answer=checkpoint_data["correct_answer"],
                    explanation=checkpoint_data["explanation"],
                    difficulty_level=getattr(DifficultyLevel, checkpoint_data["difficulty_level"].upper()),
                    order_index=checkpoint_data["order_index"],
                    points=checkpoint_data["points"],
                    time_limit_seconds=checkpoint_data["time_limit_seconds"]
                )
                db.add(checkpoint)
                print(f"    Created checkpoint: {checkpoint_data['question'][:50]}...")
    
    db.commit()

def seed_physics_content(db: Session, course_id: int):
    """Create sample physics content."""
    # Create chapter
    chapter = models.Chapter(
        course_id=course_id,
        name="Mechanics",
        description="Fundamental concepts of motion, force, and energy",
        order_index=1,
        estimated_hours=10
    )
    db.add(chapter)
    db.flush()
    
    # Create topic
    topic = models.Topic(
        chapter_id=chapter.id,
        name="Newton's Laws of Motion",
        description="Understanding the three fundamental laws of motion",
        order_index=1,
        estimated_time_minutes=120,
        difficulty_level=DifficultyLevel.MEDIUM
    )
    db.add(topic)
    db.flush()
    
    # Create content block
    content_block = models.ContentBlock(
        topic_id=topic.id,
        title="Introduction to Newton's Laws",
        content="""# Newton's Laws of Motion

Sir Isaac Newton formulated three fundamental laws that describe the relationship between forces and motion:

## First Law (Law of Inertia)
An object at rest stays at rest and an object in motion stays in motion with the same speed and in the same direction unless acted upon by an unbalanced force.

## Second Law
The acceleration of an object is directly proportional to the net force acting on it and inversely proportional to its mass.
**F = ma**

## Third Law
For every action, there is an equal and opposite reaction.

These laws form the foundation of classical mechanics and are essential for understanding motion in the physical world.""",
        content_type="explanation",
        order_index=1
    )
    db.add(content_block)
    
    # Create checkpoint
    checkpoint = models.Checkpoint(
        topic_id=topic.id,
        question="According to Newton's second law, if the mass of an object is doubled while keeping the force constant, what happens to acceleration?",
        question_type=QuestionType.MCQ,
        options=["A) Doubles", "B) Halves", "C) Remains same", "D) Becomes zero"],
        correct_answer="B",
        explanation="According to F = ma, if F is constant and m is doubled, then a = F/(2m) = (1/2)(F/m), so acceleration becomes half.",
        difficulty_level=DifficultyLevel.MEDIUM,
        order_index=1,
        points=2,
        time_limit_seconds=90
    )
    db.add(checkpoint)
    
    db.commit()
    print("Created sample Physics content")

def seed_chemistry_content(db: Session, course_id: int):
    """Create sample chemistry content."""
    # Create chapter
    chapter = models.Chapter(
        course_id=course_id,
        name="Atomic Structure",
        description="Structure of atoms and electronic configuration",
        order_index=1,
        estimated_hours=8
    )
    db.add(chapter)
    db.flush()
    
    # Create topic
    topic = models.Topic(
        chapter_id=chapter.id,
        name="Electronic Configuration",
        description="Distribution of electrons in atomic orbitals",
        order_index=1,
        estimated_time_minutes=90,
        difficulty_level=DifficultyLevel.MEDIUM
    )
    db.add(topic)
    db.flush()
    
    # Create content block
    content_block = models.ContentBlock(
        topic_id=topic.id,
        title="Understanding Electronic Configuration",
        content="""# Electronic Configuration

Electronic configuration describes the distribution of electrons in atomic orbitals.

## Key Principles:

1. **Aufbau Principle**: Electrons fill orbitals in order of increasing energy
2. **Pauli Exclusion Principle**: No two electrons can have the same set of quantum numbers
3. **Hund's Rule**: Electrons fill degenerate orbitals singly before pairing

## Orbital Order:
1s < 2s < 2p < 3s < 3p < 4s < 3d < 4p < 5s < 4d < 5p...

## Examples:
- Hydrogen (H): 1s¹
- Carbon (C): 1s² 2s² 2p²
- Oxygen (O): 1s² 2s² 2p⁴""",
        content_type="explanation",
        order_index=1
    )
    db.add(content_block)
    
    # Create checkpoint
    checkpoint = models.Checkpoint(
        topic_id=topic.id,
        question="What is the electronic configuration of Nitrogen (atomic number 7)?",
        question_type=QuestionType.MCQ,
        options=["A) 1s² 2s² 2p³", "B) 1s² 2s² 2p⁵", "C) 1s² 2s³ 2p²", "D) 1s² 2p⁵"],
        correct_answer="A",
        explanation="Nitrogen has 7 electrons. Following Aufbau principle: 1s² (2 electrons) + 2s² (2 electrons) + 2p³ (3 electrons) = 7 total electrons.",
        difficulty_level=DifficultyLevel.EASY,
        order_index=1,
        points=1,
        time_limit_seconds=60
    )
    db.add(checkpoint)
    
    db.commit()
    print("Created sample Chemistry content")

def main():
    """Main seeding function."""
    print("Starting database seeding...")
    
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create sample users
        print("\n1. Creating sample users...")
        create_sample_users(db)
        
        # Create courses
        print("\n2. Creating courses...")
        courses = create_courses(db)
        
        # Seed math content from JSON
        print("\n3. Seeding Mathematics content...")
        math_json_path = "../content/jee_courses/math/algebra.json"
        if os.path.exists(math_json_path):
            seed_content_from_json(db, math_json_path, courses["MATH_JEE"].id)
        else:
            print(f"Warning: Math content file not found at {math_json_path}")
        
        # Create sample physics content
        print("\n4. Creating Physics content...")
        seed_physics_content(db, courses["PHYS_JEE"].id)
        
        # Create sample chemistry content
        print("\n5. Creating Chemistry content...")
        seed_chemistry_content(db, courses["CHEM_JEE"].id)
        
        print("\n✅ Database seeding completed successfully!")
        print("\n📚 Sample users created:")
        print("  - Student: student@jee.com / password123")
        print("  - Teacher: teacher@jee.com / password123")
        print("  - Admin: admin@jee.com / password123")
        
        print("\n📖 Courses created:")
        print("  - Mathematics (with Algebra chapter)")
        print("  - Physics (with Mechanics chapter)")
        print("  - Chemistry (with Atomic Structure chapter)")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()