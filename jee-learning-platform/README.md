# JEE Learning Platform

A comprehensive, AI-powered adaptive learning platform for JEE Main preparation featuring intelligent analytics, personalized quizzes, and detailed progress tracking.

## 🎯 Overview

This platform provides an end-to-end solution for JEE Main preparation with:

- **Adaptive Learning**: AI-powered personalized quizzes based on user weaknesses
- **Comprehensive Analytics**: Detailed progress tracking and mastery assessment
- **Structured Content**: Complete JEE syllabus coverage with interactive content
- **Session Management**: Time tracking and study pattern analysis
- **Progress Visualization**: Real-time progress bars and performance metrics

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **API Framework**: FastAPI with automatic OpenAPI documentation
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based authentication with role-based access
- **AI Integration**: OpenAI GPT for adaptive quiz generation
- **Analytics Engine**: Comprehensive tracking and reporting system

### Frontend (Next.js + TypeScript)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with responsive design
- **UI Components**: Radix UI primitives for accessibility
- **State Management**: React hooks with API integration
- **Type Safety**: Full TypeScript implementation

### Key Features

#### 📚 Content Management
- Structured courses (Math, Physics, Chemistry)
- Hierarchical organization (Course → Chapter → Topic → Content Blocks)
- Interactive checkpoints with immediate feedback
- Markdown support for rich content formatting

#### 🧠 Adaptive Learning System
- AI-generated quizzes targeting user's weak areas
- Difficulty adjustment based on performance
- Multiple quiz types (weakness focus, speed practice, comprehensive review)
- Personalized learning path recommendations

#### 📊 Analytics & Tracking
- Real-time progress monitoring
- Mastery level calculation (Not Started → Weak → Average → Strong → Mastered)
- Study pattern analysis (daily/weekly reports)
- Session tracking with time management

#### 🎯 Personalization
- Individual learning paths based on performance data
- Customized study plans with time recommendations
- Weakness identification and targeted practice
- Progress visualization with intuitive charts

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

### Backend Setup

1. **Clone and navigate to backend**
```bash
git clone <repository-url>
cd jee-learning-platform/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your database credentials and API keys
```

5. **Database setup**
```bash
# Create PostgreSQL database
createdb jee_learning_db

# Run database migrations
python seed_data.py  # This creates tables and seeds sample data
```

6. **Start the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Environment configuration**
```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

4. **Start development server**
```bash
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Sample Accounts
```
Student: student@jee.com / password123
Teacher: teacher@jee.com / password123
Admin: admin@jee.com / password123
```

## 📁 Project Structure

```
jee-learning-platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models/
│   │   │   ├── models.py        # SQLAlchemy database models
│   │   │   └── schemas.py       # Pydantic schemas for API
│   │   ├── routes/
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── content.py       # Content management endpoints
│   │   │   ├── analytics.py     # Analytics and reporting endpoints
│   │   │   └── ai.py            # AI-powered features endpoints
│   │   ├── services/
│   │   │   ├── analytics_service.py  # Analytics business logic
│   │   │   └── ai_service.py         # AI integration and quiz generation
│   │   ├── utils/
│   │   │   └── auth.py          # Authentication utilities
│   │   └── database/
│   │       └── database.py      # Database connection configuration
│   ├── requirements.txt         # Python dependencies
│   ├── seed_data.py            # Database seeding script
│   └── .env.example            # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # Root layout component
│   │   │   ├── page.tsx         # Homepage
│   │   │   └── globals.css      # Global styles
│   │   ├── lib/
│   │   │   ├── api.ts           # API configuration and functions
│   │   │   └── utils.ts         # Utility functions
│   │   └── components/          # Reusable React components
│   ├── package.json             # Node.js dependencies
│   └── tailwind.config.ts       # Tailwind CSS configuration
├── content/
│   └── jee_courses/
│       ├── math/
│       │   └── algebra.json     # Sample mathematics content
│       ├── physics/             # Physics content structure
│       └── chemistry/           # Chemistry content structure
└── README.md                    # This file
```

## 🔧 Configuration

### Backend Configuration (.env)
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/jee_learning_db

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Integration (Optional)
OPENAI_API_KEY=your-openai-api-key

# App Settings
DEBUG=True
FRONTEND_URL=http://localhost:3000
```

### Frontend Configuration (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/token` - User login
- `GET /auth/me` - Get current user
- `PUT /auth/me` - Update user profile

### Content Management
- `GET /content/courses` - Get courses with navigation
- `GET /content/topics/{id}` - Get topic content
- `POST /content/checkpoints/{id}/answer` - Submit checkpoint answer
- `POST /content/topics/{id}/time-tracking` - Track study time

### Analytics
- `GET /analytics/dashboard` - User dashboard data
- `GET /analytics/progress` - User progress data
- `GET /analytics/weekly-report` - Weekly performance report
- `GET /analytics/study-pattern` - Study pattern analysis

### AI Features
- `POST /ai/generate-quiz` - Generate adaptive quiz
- `POST /ai/submit-quiz/{id}` - Submit quiz answers
- `GET /ai/learning-path` - Get personalized learning path
- `GET /ai/recommendations` - Get study recommendations

## 🎨 Features in Detail

### 1. Adaptive Learning System
The AI system analyzes user performance to:
- Identify weak topics and concepts
- Generate targeted practice questions
- Adjust difficulty based on user capability
- Provide personalized study recommendations

### 2. Mastery Tracking
Each topic has a mastery level calculated from:
- **Accuracy**: Percentage of correct answers
- **Speed**: Time taken relative to expected time
- **Consistency**: Performance across multiple attempts
- **Confidence Score**: Combined metric (0.0 to 1.0)

### 3. Progress Analytics
Comprehensive tracking includes:
- Time spent per topic/chapter/course
- Completion percentages at all levels
- Study pattern analysis (daily/weekly trends)
- Performance comparison over time

### 4. Content Structure
- **Courses**: Math, Physics, Chemistry
- **Chapters**: Major topic divisions
- **Topics**: Specific concepts within chapters
- **Content Blocks**: Explanations, examples, formulas
- **Checkpoints**: Interactive quizzes and assessments

## 🔄 Development Workflow

### Adding New Content
1. Create JSON files in `content/jee_courses/`
2. Run `python seed_data.py` to import content
3. Content automatically appears in the navigation

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🚀 Production Deployment

### Backend Deployment
```bash
# Using Docker
docker build -t jee-backend .
docker run -p 8000:8000 jee-backend

# Or using cloud services
# Configure DATABASE_URL for production database
# Set SECRET_KEY to a secure random string
# Configure OPENAI_API_KEY for AI features
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Deploy to Vercel, Netlify, or other platforms
# Configure NEXT_PUBLIC_API_URL to point to production backend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the [API documentation](http://localhost:8000/docs)
- Review the codebase for implementation details

## 🔮 Future Enhancements

- [ ] Mobile application (React Native)
- [ ] Advanced analytics dashboard
- [ ] Video content integration
- [ ] Discussion forums and community features
- [ ] Advanced AI tutoring capabilities
- [ ] Exam simulation mode
- [ ] Performance comparison with peers
- [ ] Gamification elements (badges, leaderboards)

---

**Happy Learning! 🎓**