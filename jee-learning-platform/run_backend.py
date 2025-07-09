#!/usr/bin/env python3
"""
Quick start script for JEE Learning Platform backend
This script sets up the environment and starts the backend server
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🎓 JEE Learning Platform - Backend Startup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def setup_environment():
    """Set up the environment"""
    print("\n📦 Setting up environment...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Creating .env file from template...")
        env_example = Path(".env.example")
        if env_example.exists():
            # Copy .env.example to .env with SQLite for quick start
            with open(env_example, 'r') as f:
                content = f.read()
            
            # Replace PostgreSQL with SQLite for quick start
            content = content.replace(
                "DATABASE_URL=postgresql://username:password@localhost:5432/jee_learning_db",
                "DATABASE_URL=sqlite:///./jee_learning.db"
            )
            
            with open(".env", 'w') as f:
                f.write(content)
            print("✅ .env file created with SQLite database")
        else:
            print("❌ .env.example file not found")
            return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def setup_database():
    """Set up and seed the database"""
    print("\n🗄️  Setting up database...")
    try:
        # Import and run the seeding script
        sys.path.append(".")
        import seed_data
        print("✅ Database setup completed")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting FastAPI server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 40)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def test_api():
    """Test if the API is running"""
    print("\n🧪 Testing API...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running correctly")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ API test failed with status: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def show_next_steps():
    """Show next steps to the user"""
    print("\n" + "=" * 60)
    print("🎉 Backend is now running!")
    print("=" * 60)
    print()
    print("📍 URLs:")
    print("   • Backend API: http://localhost:8000")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    print()
    print("👤 Sample Accounts:")
    print("   • Student: student@jee.com / password123")
    print("   • Teacher: teacher@jee.com / password123")
    print("   • Admin: admin@jee.com / password123")
    print()
    print("🚀 Next Steps:")
    print("   1. Open another terminal")
    print("   2. cd jee-learning-platform/frontend")
    print("   3. npm install")
    print("   4. npm run dev")
    print("   5. Open http://localhost:3000")
    print()
    print("📚 Sample Content Available:")
    print("   • Mathematics: Algebra (Quadratic Equations, Complex Numbers, Sequences)")
    print("   • Physics: Mechanics (Newton's Laws)")
    print("   • Chemistry: Atomic Structure (Electronic Configuration)")
    print()

def main():
    """Main execution function"""
    print_banner()
    
    # Check requirements
    if not check_python_version():
        return 1
    
    # Setup environment
    if not setup_environment():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Setup database
    if not setup_database():
        return 1
    
    # Show next steps before starting server
    show_next_steps()
    
    # Start the server
    start_server()
    
    return 0

if __name__ == "__main__":
    exit(main())