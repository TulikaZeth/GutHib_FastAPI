# 🧠 Resume Intelligence Analyzer

An AI-powered backend service built with **FastAPI** and **Google Gemini** that automatically analyzes and interprets resumes **AND GitHub profiles**. The system extracts key technical skills, experience, and technology categories from uploaded resumes (PDF, DOCX, or TXT) and analyzes GitHub repositories to provide scored, structured, and explainable outputs.

## 🎯 Project Objective

Build an intelligent API that:
- ✅ Accepts resume files in multiple formats
- 🔍 Extracts and preprocesses text content
- 🐙 Analyzes GitHub profiles and repositories
- 🤖 Uses Google Gemini's large language model for analysis
- 📊 Returns structured insights with confidence scores
- 🏆 Provides skill scoring (1-10 scale) for ranking and matching
- 🎯 Cross-validates skills between resume and GitHub activity

## 🏗️ Architecture

### 1️⃣ **Text Extraction Layer** (`extractors.py`)
- **Purpose:** Accept resumes in different formats
- **Supported Formats:** PDF, DOCX, TXT
- **Output:** Raw text content
- **Technologies:** PyPDF2, python-docx

### 2️⃣ **Text Preprocessing Layer** (`preprocessor.py`)
- **Purpose:** Clean and normalize text for AI analysis
- **Operations:**
  - Remove extra whitespace
  - Clean special characters
  - Preserve structure (headings, bullets)
- **Technologies:** Python regex (re)

### 3️⃣ **AI Analysis Layer** (`gemini_analyzer.py`)
- **Purpose:** Leverage Google Gemini for intelligent extraction
- **Capabilities:**
  - Identify skills and technologies
  - Assess skill prominence and frequency
  - Estimate experience duration
  - Categorize technologies (Languages, Frameworks, Tools, Libraries)
- **Output:** Structured JSON with confidence scores

### 4️⃣ **Skill Scoring Mechanism**
Gemini assigns scores from **1-10** for each skill:
- **9-10:** Very prominent, deeply integrated
- **6-8:** Moderate frequency, practical experience
- **3-5:** Mentioned once or twice
- **1-2:** Inferred or minimal mention

### 5️⃣ **API Layer** (`main.py`)
- **Framework:** FastAPI
- **Primary Endpoint:** `POST /analyze`
- **Features:**
  - File upload handling
  - Error handling and validation
  - Structured JSON responses
  - Interactive API documentation

## 📋 API Endpoints

### `POST /analyze`
**Main endpoint for resume analysis**

**Request:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf"
```

### `GET /analyze/github/{username}`
**NEW: GitHub profile analysis endpoint**

**Request:**
```bash
curl -X GET "http://localhost:8000/analyze/github/tulika-anand"
```

**Response:**
```json
{
  "status": "success",
  "username": "tulika-anand",
  "github_url": "https://github.com/tulika-anand",
  "user_info": {
    "name": "Tulika Anand",
    "bio": "Software Engineer | AI/ML Enthusiast",
    "followers": 150,
    "public_repos": 25
  },
  "stats": {
    "languages_used": {"Python": 12, "JavaScript": 8, "Java": 5},
    "total_stars_earned": 420,
    "total_forks": 38
  },
  "analysis": {
    "overall_experience_level": "Intermediate",
    "experience_years_estimate": 2.5,
    "skills_with_scores": {
      "Python": 9,
      "React": 8,
      "FastAPI": 7,
      "Machine Learning": 8
    },
    "dominant_tech_stack": {
      "languages": ["Python", "JavaScript"],
      "frameworks": ["React", "FastAPI", "Django"],
      "domains": ["AI/ML", "Web Development"]
    },
    "project_analysis": {
      "notable_projects": [
        {
          "name": "PharmLensAI",
          "description": "AI-powered lab report analyzer",
          "complexity_score": 9,
          "impact_score": 8,
          "technologies": ["Python", "TensorFlow", "FastAPI"],
          "stars": 45
        }
      ]
    },
    "strengths": ["Strong Python expertise", "Active in AI/ML domain"],
    "areas_for_growth": ["Contribute to more open-source projects"]
  }
}
```

### `POST /analyze/combined`
**NEW: Combined resume + GitHub analysis**

**Request:**
```bash
curl -X POST "http://localhost:8000/analyze/combined?github_username=tulika-anand" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf"
```

**Use Cases:**
- Complete candidate assessment
- Cross-validate resume claims with GitHub activity
- Comprehensive technical profile evaluation

### `POST /extract-text`
**Utility endpoint for text extraction only**

### `GET /health`
**Health check endpoint**

### `GET /` and `GET /docs`
**API documentation**

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Google Gemini API Key

### Installation

1. **Clone the repository:**
```bash
cd c:\Users\acer\projects\GutHib
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your Google API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

4. **Get Google Gemini API Key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file

### Running the Application

**Development mode:**
```bash
python main.py
```

**Or using uvicorn directly:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- 🌐 API: http://localhost:8000
- 📚 Interactive Docs: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc

## 📁 Project Structure

```
GutHib/
├── main.py                 # FastAPI application & endpoints
├── config.py              # Configuration management
├── models.py              # Pydantic models for validation
├── extractors.py          # Text extraction from files
├── preprocessor.py        # Text cleaning & preprocessing
├── gemini_analyzer.py     # Gemini AI integration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── uploads/              # Temporary file storage (auto-created)
```

## 🧪 Testing the API

### Using cURL:
```bash
# Analyze a PDF resume
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_resume.pdf"

# Analyze GitHub profile
curl http://localhost:8000/analyze/github/tulika-anand

# Combined analysis
curl -X POST "http://localhost:8000/analyze/combined?github_username=tulika-anand" \
  -F "file=@resume.pdf"

# Health check
curl http://localhost:8000/health
```

### Using Python:
```python
import requests

# Resume analysis
url = "http://localhost:8000/analyze"
files = {"file": open("resume.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())

# GitHub analysis
url = "http://localhost:8000/analyze/github/tulika-anand"
response = requests.get(url)
print(response.json())
```

### Using Test Scripts:
```bash
# Test resume analysis
python test_sample.py

# Test GitHub analysis
python test_github.py
```

### Using the Interactive Docs:
Navigate to http://localhost:8000/docs and use the built-in interface to test all endpoints.

## 🔧 Configuration

Edit `config.py` or `.env` file:

```python
# Google Gemini
GOOGLE_API_KEY=your_key_here

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
```

## 🎯 Use Cases

1. **Recruitment Automation:** Automatically screen and rank candidates
2. **Skill Matching:** Match candidates to job requirements
3. **Resume Optimization:** Provide feedback to job seekers
4. **Talent Analytics:** Generate insights on candidate pools
5. **ATS Integration:** Enhance applicant tracking systems
6. **🆕 GitHub Profile Verification:** Validate resume claims with actual code
7. **🆕 Developer Assessment:** Evaluate coding activity and project complexity
8. **🆕 Technical Screening:** Automated technical candidate evaluation
9. **🆕 Portfolio Analysis:** Assess real-world project experience

## 🛣️ Roadmap

- [ ] Add resume comparison feature
- [ ] Implement job description matching
- [ ] Add support for more file formats
- [ ] Create visualization dashboard
- [ ] Add database for storing analysis results
- [ ] Implement batch processing
- [ ] Add authentication/authorization
- [ ] Deploy as containerized service

## ⚠️ Notes

- Files are temporarily stored and automatically deleted after processing
- Maximum file size: 10MB (configurable)
- Gemini API usage is subject to Google's quotas and pricing
- For production use, implement proper authentication and rate limiting

## 📝 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

**Built with ❤️ using FastAPI and Google Gemini**
