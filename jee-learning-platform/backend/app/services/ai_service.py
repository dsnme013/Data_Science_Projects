import openai
import json
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import models, schemas
from app.models.models import DifficultyLevel, QuestionType, MasteryLevel
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generate_adaptive_quiz(self, db: Session, user_id: int, 
                             quiz_request: schemas.AdaptiveQuizRequest) -> List[schemas.GeneratedQuestion]:
        """Generate adaptive quiz questions based on user's weak areas and requirements."""
        
        # Get user's mastery data for target topics
        if quiz_request.target_topics:
            target_topic_ids = quiz_request.target_topics
        else:
            # If no specific topics, get user's weak topics
            weak_topics = self._get_weak_topics(db, user_id)
            target_topic_ids = [topic.topic_id for topic in weak_topics[:5]]
        
        if not target_topic_ids:
            return []
        
        # Get topic information
        topics = db.query(models.Topic).filter(
            models.Topic.id.in_(target_topic_ids)
        ).all()
        
        # Generate questions for each topic
        generated_questions = []
        questions_per_topic = max(1, quiz_request.num_questions // len(topics))
        
        for topic in topics:
            # Get topic content for context
            content_blocks = db.query(models.ContentBlock).filter(
                models.ContentBlock.topic_id == topic.id
            ).all()
            
            topic_content = "\n".join([block.content for block in content_blocks])
            
            # Get user's mastery level for this topic
            mastery = db.query(models.MasteryTracking).filter(
                models.MasteryTracking.user_id == user_id,
                models.MasteryTracking.topic_id == topic.id
            ).first()
            
            difficulty = self._determine_difficulty(mastery, quiz_request.difficulty_level)
            
            # Generate questions for this topic
            topic_questions = self._generate_questions_for_topic(
                topic, topic_content, difficulty, questions_per_topic, quiz_request.quiz_type
            )
            generated_questions.extend(topic_questions)
        
        return generated_questions[:quiz_request.num_questions]
    
    def _get_weak_topics(self, db: Session, user_id: int) -> List[models.MasteryTracking]:
        """Get user's weak topics for targeted practice."""
        return db.query(models.MasteryTracking).filter(
            models.MasteryTracking.user_id == user_id,
            models.MasteryTracking.mastery_level.in_([MasteryLevel.WEAK, MasteryLevel.NOT_STARTED])
        ).order_by(models.MasteryTracking.confidence_score).all()
    
    def _determine_difficulty(self, mastery: Optional[models.MasteryTracking], 
                            requested_difficulty: Optional[DifficultyLevel]) -> DifficultyLevel:
        """Determine appropriate difficulty based on mastery level."""
        if requested_difficulty:
            return requested_difficulty
        
        if not mastery:
            return DifficultyLevel.EASY
        
        if mastery.mastery_level == MasteryLevel.WEAK:
            return DifficultyLevel.EASY
        elif mastery.mastery_level == MasteryLevel.AVERAGE:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.HARD
    
    def _generate_questions_for_topic(self, topic: models.Topic, content: str, 
                                    difficulty: DifficultyLevel, num_questions: int,
                                    quiz_type: str) -> List[schemas.GeneratedQuestion]:
        """Generate questions for a specific topic using OpenAI."""
        
        if not self.openai_api_key:
            # Fallback to sample questions if no API key
            return self._generate_fallback_questions(topic, difficulty, num_questions)
        
        system_prompt = self._get_system_prompt(quiz_type, difficulty)
        user_prompt = self._get_user_prompt(topic, content, num_questions)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            questions_text = response.choices[0].message.content
            return self._parse_generated_questions(questions_text, topic.id, difficulty)
            
        except Exception as e:
            print(f"Error generating questions with OpenAI: {e}")
            return self._generate_fallback_questions(topic, difficulty, num_questions)
    
    def _get_system_prompt(self, quiz_type: str, difficulty: DifficultyLevel) -> str:
        """Get system prompt based on quiz type and difficulty."""
        base_prompt = """You are an expert JEE Main exam question generator. Generate high-quality multiple choice questions (MCQs) that test conceptual understanding and problem-solving skills."""
        
        difficulty_guidance = {
            DifficultyLevel.EASY: "Focus on basic concepts and direct applications. Questions should test fundamental understanding.",
            DifficultyLevel.MEDIUM: "Include moderate complexity with some multi-step problem solving. Test application of concepts.",
            DifficultyLevel.HARD: "Create challenging problems requiring deep understanding and multi-concept integration. Include tricky scenarios."
        }
        
        quiz_type_guidance = {
            "weakness_focus": "Focus on common misconceptions and areas where students typically struggle.",
            "speed_practice": "Create questions that can be solved quickly with the right approach. Focus on pattern recognition.",
            "comprehensive_review": "Cover diverse aspects of the topic with varying difficulty levels."
        }
        
        return f"""{base_prompt}
        
        Difficulty Level: {difficulty_guidance.get(difficulty, "")}
        Quiz Type: {quiz_type_guidance.get(quiz_type, "")}
        
        Format each question as JSON with this structure:
        {{
            "question": "Question text here",
            "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
            "correct_answer": "A",
            "explanation": "Detailed explanation of why this is correct"
        }}
        
        Return a JSON array of questions. Make sure all questions are accurate and educational."""
    
    def _get_user_prompt(self, topic: models.Topic, content: str, num_questions: int) -> str:
        """Get user prompt with topic context."""
        return f"""Generate {num_questions} JEE Main level multiple choice questions for the topic: "{topic.name}"

        Topic Description: {topic.description}
        
        Content Context:
        {content[:1500]}...
        
        Please generate questions that test understanding of this specific topic. Make sure questions are:
        1. Aligned with JEE Main syllabus
        2. Clear and unambiguous
        3. Have exactly one correct answer
        4. Include detailed explanations
        
        Return the questions as a JSON array."""
    
    def _parse_generated_questions(self, questions_text: str, topic_id: int, 
                                 difficulty: DifficultyLevel) -> List[schemas.GeneratedQuestion]:
        """Parse OpenAI generated questions into structured format."""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', questions_text, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
            else:
                questions_data = json.loads(questions_text)
            
            parsed_questions = []
            for q_data in questions_data:
                question = schemas.GeneratedQuestion(
                    question=q_data["question"],
                    question_type=QuestionType.MCQ,
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"],
                    difficulty_level=difficulty,
                    topic_id=topic_id
                )
                parsed_questions.append(question)
            
            return parsed_questions
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing generated questions: {e}")
            return []
    
    def _generate_fallback_questions(self, topic: models.Topic, difficulty: DifficultyLevel, 
                                   num_questions: int) -> List[schemas.GeneratedQuestion]:
        """Generate fallback questions when AI service is unavailable."""
        fallback_questions = [
            {
                "question": f"Which of the following is a key concept in {topic.name}?",
                "options": ["A) Concept A", "B) Concept B", "C) Concept C", "D) All of the above"],
                "correct_answer": "D",
                "explanation": f"All the listed concepts are fundamental to understanding {topic.name}."
            },
            {
                "question": f"In the context of {topic.name}, what is the most important principle?",
                "options": ["A) Principle 1", "B) Principle 2", "C) Principle 3", "D) None of these"],
                "correct_answer": "A",
                "explanation": f"Principle 1 is fundamental to {topic.name} and forms the basis for advanced concepts."
            }
        ]
        
        generated = []
        for i in range(min(num_questions, len(fallback_questions))):
            q_data = fallback_questions[i]
            question = schemas.GeneratedQuestion(
                question=q_data["question"],
                question_type=QuestionType.MCQ,
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                difficulty_level=difficulty,
                topic_id=topic.id
            )
            generated.append(question)
        
        return generated
    
    def generate_learning_path(self, db: Session, user_id: int) -> schemas.PersonalizedLearningPath:
        """Generate a personalized learning path based on user's progress and weak areas."""
        
        # Get user analytics
        from app.services.analytics_service import AnalyticsService
        analytics = AnalyticsService.get_user_analytics(db, user_id)
        
        # Get weak topics that need attention
        weak_topics = analytics["weak_topics"]
        
        # Generate learning path items
        learning_items = []
        for i, topic_data in enumerate(weak_topics[:10]):  # Top 10 priorities
            topic = db.query(models.Topic).filter(
                models.Topic.id == topic_data["topic_id"]
            ).first()
            
            if topic:
                # Determine reason and priority
                confidence = topic_data["confidence_score"]
                if confidence < 0.3:
                    reason = "Critical weakness - requires immediate attention"
                    priority = 1
                elif confidence < 0.6:
                    reason = "Below average understanding - needs practice"
                    priority = 2
                else:
                    reason = "Room for improvement"
                    priority = 3
                
                learning_item = schemas.LearningPathItem(
                    topic_id=topic.id,
                    topic_name=topic.name,
                    reason=reason,
                    priority=priority,
                    estimated_time_minutes=topic.estimated_time_minutes or 45
                )
                learning_items.append(learning_item)
        
        # Generate study plan
        study_plan = self._generate_study_plan(learning_items, analytics)
        
        # Generate tips
        tips = self._generate_study_tips(analytics)
        
        return schemas.PersonalizedLearningPath(
            user_id=user_id,
            generated_at=models.func.now(),
            recommended_topics=learning_items,
            study_plan=study_plan,
            tips=tips
        )
    
    def _generate_study_plan(self, learning_items: List[schemas.LearningPathItem], 
                           analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured study plan."""
        total_time = sum(item.estimated_time_minutes for item in learning_items)
        
        # Organize by priority
        high_priority = [item for item in learning_items if item.priority == 1]
        medium_priority = [item for item in learning_items if item.priority == 2]
        low_priority = [item for item in learning_items if item.priority == 3]
        
        return {
            "total_estimated_hours": total_time / 60,
            "recommended_daily_minutes": min(120, total_time / 7),  # Spread over a week
            "weekly_plan": {
                "week_1": {
                    "focus": "Critical weaknesses",
                    "topics": [item.topic_name for item in high_priority[:3]]
                },
                "week_2": {
                    "focus": "Building understanding", 
                    "topics": [item.topic_name for item in medium_priority[:3]]
                },
                "week_3": {
                    "focus": "Reinforcement and practice",
                    "topics": [item.topic_name for item in low_priority[:3]]
                }
            },
            "study_strategy": "Focus on understanding concepts before moving to practice problems"
        }
    
    def _generate_study_tips(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate personalized study tips based on analytics."""
        tips = [
            "Break study sessions into 25-30 minute focused blocks with 5-minute breaks",
            "Review previous topics regularly to maintain retention",
            "Practice explaining concepts in your own words"
        ]
        
        if analytics["average_confidence"] < 0.5:
            tips.append("Focus on understanding fundamental concepts before attempting practice problems")
        
        if len(analytics["weak_topics"]) > 7:
            tips.append("Don't try to tackle all weak topics at once - focus on 2-3 at a time")
        
        if analytics["total_study_time_minutes"] < 300:  # Less than 5 hours total
            tips.append("Consistency is key - try to study a little bit every day rather than long sessions")
        
        return tips