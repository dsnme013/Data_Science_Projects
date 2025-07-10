import axios from 'axios';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: 'student' | 'teacher' | 'admin';
  target_exam_year?: number;
  current_class?: string;
  created_at: string;
}

export interface Course {
  id: number;
  name: string;
  code: string;
  description?: string;
  completion_percentage: number;
  chapters: Chapter[];
}

export interface Chapter {
  id: number;
  name: string;
  order_index: number;
  completion_percentage: number;
  topics: Topic[];
}

export interface Topic {
  id: number;
  name: string;
  order_index: number;
  completion_percentage: number;
  mastery_level: 'not_started' | 'weak' | 'average' | 'strong' | 'mastered';
  estimated_time_minutes?: number;
}

export interface TopicContent {
  topic: {
    id: number;
    name: string;
    description: string;
    difficulty_level: string;
    estimated_time_minutes?: number;
  };
  content_blocks: ContentBlock[];
  checkpoints: Checkpoint[];
  user_progress?: UserProgress;
  mastery_tracking?: MasteryTracking;
}

export interface ContentBlock {
  id: number;
  title: string;
  content: string;
  content_type: string;
  order_index: number;
  media_urls?: string[];
}

export interface Checkpoint {
  id: number;
  question: string;
  question_type: 'mcq' | 'numerical' | 'subjective';
  options?: string[];
  difficulty_level: string;
  order_index: number;
  points: number;
  time_limit_seconds: number;
}

export interface UserProgress {
  id: number;
  topic_id: number;
  completion_percentage: number;
  time_spent_minutes: number;
  is_completed: boolean;
  last_accessed?: string;
}

export interface MasteryTracking {
  id: number;
  topic_id: number;
  mastery_level: string;
  confidence_score: number;
  total_attempts: number;
  correct_attempts: number;
}

export interface Analytics {
  total_topics: number;
  completed_topics: number;
  completion_percentage: number;
  total_study_time_minutes: number;
  weak_topics: TopicAnalytics[];
  strong_topics: TopicAnalytics[];
  average_confidence: number;
}

export interface TopicAnalytics {
  topic_id: number;
  topic_name: string;
  mastery_level: string;
  confidence_score: number;
  accuracy: number;
}

export interface AdaptiveQuiz {
  id: number;
  quiz_type: string;
  target_topics: number[];
  generated_questions: GeneratedQuestion[];
  created_at: string;
}

export interface GeneratedQuestion {
  question: string;
  question_type: string;
  options?: string[];
  correct_answer: string;
  explanation: string;
  difficulty_level: string;
  topic_id: number;
}

// API Functions
export const authAPI = {
  register: (userData: {
    email: string;
    username: string;
    full_name: string;
    password: string;
    target_exam_year?: number;
    current_class?: string;
  }) => api.post('/auth/register', userData),

  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/token', credentials, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),

  getCurrentUser: () => api.get<User>('/auth/me'),

  updateProfile: (userData: Partial<User>) => api.put('/auth/me', userData),
};

export const contentAPI = {
  getCourses: () => api.get<Course[]>('/content/courses'),
  
  getTopicContent: (topicId: number) => 
    api.get<TopicContent>(`/content/topics/${topicId}`),

  submitAnswer: (checkpointId: number, answer: {
    user_answer: string;
    time_taken_seconds?: number;
  }) => api.post(`/content/checkpoints/${checkpointId}/answer`, answer),

  trackTime: (topicId: number, timeSpent: number) =>
    api.post(`/content/topics/${topicId}/time-tracking`, null, {
      params: { time_spent_minutes: timeSpent }
    }),

  endSession: (sessionId: number, actionsData?: any) =>
    api.post(`/content/sessions/${sessionId}/end`, { 
      session_id: sessionId,
      actions_taken: actionsData 
    }),
};

export const analyticsAPI = {
  getDashboard: () => api.get('/analytics/dashboard'),
  
  getUserProgress: () => api.get<UserProgress[]>('/analytics/progress'),
  
  getTopicAnalytics: (topicId: number) => 
    api.get(`/analytics/topic-analytics/${topicId}`),
    
  getWeeklyReport: (weekStart: string) =>
    api.get('/analytics/weekly-report', { params: { week_start: weekStart } }),
    
  getStudyPattern: (days = 30) =>
    api.get('/analytics/study-pattern', { params: { days } }),
};

export const aiAPI = {
  generateQuiz: (request: {
    quiz_type: string;
    target_topics?: number[];
    difficulty_level?: string;
    num_questions?: number;
  }) => api.post<AdaptiveQuiz>('/ai/generate-quiz', request),

  submitQuiz: (quizId: number, answers: any[]) =>
    api.post(`/ai/submit-quiz/${quizId}`, { 
      quiz_id: quizId,
      answers 
    }),

  getLearningPath: () => api.get('/ai/learning-path'),

  getRecommendations: () => api.get('/ai/recommendations'),

  getQuizHistory: () => api.get('/ai/quiz-history'),

  generateStudyPlan: (days = 7, dailyMinutes = 60) =>
    api.post('/ai/study-plan/generate', null, {
      params: { days, daily_minutes: dailyMinutes }
    }),
};