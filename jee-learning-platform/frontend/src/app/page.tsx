'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  BookOpen, 
  Brain, 
  TrendingUp, 
  Users, 
  Award, 
  Target,
  ChevronRight,
  Play,
  BarChart3,
  Zap
} from 'lucide-react';

export default function HomePage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
  }, []);

  const features = [
    {
      icon: <Brain className="h-8 w-8" />,
      title: "AI-Powered Adaptive Learning",
      description: "Personalized quizzes that adapt to your strengths and weaknesses for optimal learning",
      color: "text-purple-600"
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Comprehensive Analytics",
      description: "Track your progress with detailed analytics and mastery assessments",
      color: "text-blue-600"
    },
    {
      icon: <Target className="h-8 w-8" />,
      title: "Focused Practice",
      description: "Target your weak areas with automatically generated practice problems",
      color: "text-green-600"
    },
    {
      icon: <Zap className="h-8 w-8" />,
      title: "Speed & Accuracy Training",
      description: "Improve your problem-solving speed with timed practice sessions",
      color: "text-yellow-600"
    }
  ];

  const subjects = [
    { name: "Mathematics", topics: 25, icon: "📐", color: "bg-blue-100 text-blue-800" },
    { name: "Physics", topics: 22, icon: "⚡", color: "bg-purple-100 text-purple-800" },
    { name: "Chemistry", topics: 28, icon: "🧪", color: "bg-green-100 text-green-800" }
  ];

  const stats = [
    { label: "Active Students", value: "10,000+", icon: <Users className="h-6 w-6" /> },
    { label: "Practice Questions", value: "50,000+", icon: <BookOpen className="h-6 w-6" /> },
    { label: "Success Rate", value: "95%", icon: <Award className="h-6 w-6" /> },
    { label: "Average Improvement", value: "40%", icon: <TrendingUp className="h-6 w-6" /> }
  ];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="bg-blue-600 text-white p-2 rounded-lg">
                <BookOpen className="h-6 w-6" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">JEE Learning Platform</h1>
            </div>
            
            <nav className="flex items-center space-x-6">
              {isAuthenticated ? (
                <>
                  <Link href="/dashboard" className="text-gray-700 hover:text-blue-600 font-medium">
                    Dashboard
                  </Link>
                  <Link href="/courses" className="text-gray-700 hover:text-blue-600 font-medium">
                    Courses
                  </Link>
                  <Link href="/analytics" className="text-gray-700 hover:text-blue-600 font-medium">
                    Analytics
                  </Link>
                  <Link href="/profile" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                    Profile
                  </Link>
                </>
              ) : (
                <>
                  <Link href="/login" className="text-gray-700 hover:text-blue-600 font-medium">
                    Login
                  </Link>
                  <Link href="/register" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                    Get Started
                  </Link>
                </>
              )}
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Master JEE Main with
              <span className="text-blue-600"> AI-Powered Learning</span>
            </h2>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Adaptive learning platform that personalizes your JEE preparation with intelligent analytics, 
              targeted practice, and comprehensive progress tracking.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {isAuthenticated ? (
                <Link 
                  href="/dashboard"
                  className="bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center"
                >
                  Continue Learning <ChevronRight className="h-5 w-5 ml-2" />
                </Link>
              ) : (
                <>
                  <Link 
                    href="/register"
                    className="bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center"
                  >
                    Start Learning <ChevronRight className="h-5 w-5 ml-2" />
                  </Link>
                  <Link 
                    href="/demo"
                    className="bg-white text-blue-600 border-2 border-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-blue-50 transition-colors flex items-center justify-center"
                  >
                    <Play className="h-5 w-5 mr-2" /> Watch Demo
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="flex justify-center mb-4">
                  <div className="bg-blue-100 text-blue-600 p-3 rounded-lg">
                    {stat.icon}
                  </div>
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose Our Platform?
            </h3>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience the future of JEE preparation with our cutting-edge features designed to maximize your success.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                <div className={`${feature.color} mb-4`}>
                  {feature.icon}
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h4>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Subjects Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Complete JEE Main Syllabus Coverage
            </h3>
            <p className="text-xl text-gray-600">
              Master all three subjects with our comprehensive course structure
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {subjects.map((subject, index) => (
              <div key={index} className="bg-gray-50 p-8 rounded-xl text-center hover:shadow-lg transition-shadow">
                <div className="text-4xl mb-4">{subject.icon}</div>
                <h4 className="text-2xl font-bold text-gray-900 mb-2">{subject.name}</h4>
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${subject.color} mb-4`}>
                  {subject.topics} Topics
                </div>
                <p className="text-gray-600 mb-6">
                  Comprehensive coverage with adaptive practice and detailed analytics
                </p>
                <Link 
                  href={`/courses/${subject.name.toLowerCase()}`}
                  className="text-blue-600 font-semibold hover:text-blue-700 flex items-center justify-center"
                >
                  Explore Topics <ChevronRight className="h-4 w-4 ml-1" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your JEE Preparation?
          </h3>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join thousands of successful students who have improved their JEE scores with our AI-powered platform.
          </p>
          
          {!isAuthenticated && (
            <Link 
              href="/register"
              className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-flex items-center"
            >
              Start Your Free Trial <ChevronRight className="h-5 w-5 ml-2" />
            </Link>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="bg-blue-600 text-white p-2 rounded-lg">
                  <BookOpen className="h-6 w-6" />
                </div>
                <h5 className="text-lg font-bold">JEE Learning Platform</h5>
              </div>
              <p className="text-gray-400">
                AI-powered adaptive learning for JEE Main success.
              </p>
            </div>
            
            <div>
              <h6 className="font-semibold mb-4">Platform</h6>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/courses" className="hover:text-white">Courses</Link></li>
                <li><Link href="/analytics" className="hover:text-white">Analytics</Link></li>
                <li><Link href="/practice" className="hover:text-white">Practice</Link></li>
                <li><Link href="/ai-tutor" className="hover:text-white">AI Tutor</Link></li>
              </ul>
            </div>
            
            <div>
              <h6 className="font-semibold mb-4">Support</h6>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/help" className="hover:text-white">Help Center</Link></li>
                <li><Link href="/contact" className="hover:text-white">Contact</Link></li>
                <li><Link href="/faq" className="hover:text-white">FAQ</Link></li>
                <li><Link href="/community" className="hover:text-white">Community</Link></li>
              </ul>
            </div>
            
            <div>
              <h6 className="font-semibold mb-4">Company</h6>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/about" className="hover:text-white">About</Link></li>
                <li><Link href="/privacy" className="hover:text-white">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-white">Terms</Link></li>
                <li><Link href="/careers" className="hover:text-white">Careers</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>&copy; 2024 JEE Learning Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
