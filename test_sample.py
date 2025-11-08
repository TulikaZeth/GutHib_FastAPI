"""
Sample test script to verify the Resume Intelligence Analyzer
Run this after starting the server to test basic functionality
"""
import requests
import json
from pathlib import Path


def test_health_check():
    """Test health check endpoint"""
    print("\n🔍 Testing health check...")
    response = requests.get("http://localhost:8000/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing root endpoint...")
    response = requests.get("http://localhost:8000/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def create_sample_resume():
    """Create a sample resume text file for testing"""
    sample_resume = """
JOHN DOE
Software Engineer | john.doe@email.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 4 years of expertise in full-stack development,
specializing in Python, React, and cloud technologies. Proven track record of
delivering scalable applications and leading development teams.

TECHNICAL SKILLS
Languages: Python, JavaScript, Java, C++, SQL
Frameworks: Django, FastAPI, React, Node.js, Spring Boot
Tools: Git, Docker, Jenkins, Kubernetes, AWS
Libraries: NumPy, Pandas, TensorFlow, PyTorch, Matplotlib
Databases: PostgreSQL, MongoDB, Redis, MySQL
Cloud Platforms: AWS (EC2, S3, Lambda), Azure, Google Cloud Platform

PROFESSIONAL EXPERIENCE

Senior Software Engineer | Tech Corp Inc. | 2021 - Present
- Led development of microservices architecture using FastAPI and Docker
- Implemented CI/CD pipelines reducing deployment time by 60%
- Mentored 5 junior developers in best practices and code review
- Developed machine learning models using TensorFlow for product recommendations

Software Developer | StartupXYZ | 2020 - 2021
- Built responsive web applications using React and Node.js
- Designed and optimized PostgreSQL databases improving query performance by 40%
- Integrated third-party APIs and payment gateways
- Collaborated with cross-functional teams in Agile environment

EDUCATION
Bachelor of Science in Computer Science | University of Technology | 2020
GPA: 3.8/4.0

PROJECTS
E-commerce Platform
- Developed full-stack application using Django and React
- Implemented Redis caching for improved performance
- Deployed on AWS using EC2 and S3

AI Chatbot
- Built NLP-based chatbot using Python and TensorFlow
- Integrated with Slack API for team communication
- Achieved 85% user satisfaction rate

CERTIFICATIONS
- AWS Certified Solutions Architect
- Google Cloud Professional Data Engineer
- Certified Kubernetes Administrator (CKA)
"""
    
    # Save to file
    file_path = "sample_resume.txt"
    with open(file_path, "w") as f:
        f.write(sample_resume)
    
    print(f"\n📝 Created sample resume: {file_path}")
    return file_path


def test_analyze_resume(file_path):
    """Test resume analysis endpoint"""
    print(f"\n🔍 Testing resume analysis with {file_path}...")
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f, "text/plain")}
            response = requests.post(
                "http://localhost:8000/analyze",
                files=files
            )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Analysis successful!")
            print(f"\nStatus: {result.get('status')}")
            print(f"Skills found: {len(result.get('skills', []))}")
            print(f"Summary: {result.get('summary', 'N/A')[:100]}...")
            
            print("\n📊 Top Skills:")
            for skill in result.get('skills', [])[:5]:
                print(f"  • {skill['name']} (Score: {skill['score']}/10) - {skill['category']}")
            
            if result.get('experience'):
                exp = result['experience']
                print(f"\n💼 Experience: {exp['total_years']} years (Confidence: {exp['confidence']})")
            
            tech_stack = result.get('tech_stack', {})
            print(f"\n🛠️ Tech Stack:")
            print(f"  Languages: {', '.join(tech_stack.get('languages', [])[:5])}")
            print(f"  Frameworks: {', '.join(tech_stack.get('frameworks', [])[:5])}")
            print(f"  Tools: {', '.join(tech_stack.get('tools', [])[:5])}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False


def test_extract_text(file_path):
    """Test text extraction endpoint"""
    print(f"\n🔍 Testing text extraction with {file_path}...")
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f, "text/plain")}
            response = requests.post(
                "http://localhost:8000/extract-text",
                files=files
            )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Extraction successful!")
            stats = result.get('statistics', {})
            print(f"Characters: {stats.get('total_characters')}")
            print(f"Words: {stats.get('total_words')}")
            print(f"Lines: {stats.get('total_lines')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Resume Intelligence Analyzer - Test Suite")
    print("=" * 60)
    print("\nMake sure the server is running on http://localhost:8000")
    print("Start server with: python main.py")
    
    input("\nPress Enter to start tests...")
    
    # Test basic endpoints
    test_root()
    test_health_check()
    
    # Create sample resume
    sample_file = create_sample_resume()
    
    # Test extraction
    test_extract_text(sample_file)
    
    # Test analysis
    test_analyze_resume(sample_file)
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)
    print(f"\nSample file created: {sample_file}")
    print("You can now test with your own resume files!")


if __name__ == "__main__":
    main()
