"""
Resume Intelligence Analyzer - FastAPI Backend
Main application entry point
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Any, Dict
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models import ResumeAnalysisResponse, ErrorResponse, Skill, ExperienceInfo, TechStack
from extractors import TextExtractor
from preprocessor import TextPreprocessor
from gemini_analyzer import GeminiAnalyzer
from github_fetcher import GitHubFetcher
from github_analyzer import GitHubProfileAnalyzer

# Initialize FastAPI app
app = FastAPI(
    title="Resume Intelligence Analyzer",
    description="AI-powered resume analysis and GitHub profile assessment using Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
try:
    settings.validate()
    gemini_analyzer = GeminiAnalyzer()
except Exception as e:
    print(f"Initialization error: {str(e)}")
    gemini_analyzer = None


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Starting Resume Intelligence Analyzer...")
    print(f"📁 Upload directory: {settings.UPLOAD_DIR}")
    print(f"🤖 Gemini model: {settings.GEMINI_MODEL}")
    
    if not gemini_analyzer:
        print("⚠️ WARNING: Gemini analyzer not initialized. Check your API key.")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "service": "Resume Intelligence Analyzer",
        "status": "online",
        "version": "1.0.0",
        "features": ["Resume Analysis", "GitHub Profile Analysis"],
        "gemini_configured": gemini_analyzer is not None
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "gemini_api": "configured" if settings.GOOGLE_API_KEY else "not configured",
        "upload_dir": os.path.exists(settings.UPLOAD_DIR),
        "supported_formats": list(settings.ALLOWED_EXTENSIONS)
    }


def validate_file(file: UploadFile) -> None:
    """
    Validate uploaded file
    
    Args:
        file: Uploaded file object
        
    Raises:
        HTTPException if validation fails
    """
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check if file is empty
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )


async def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save uploaded file temporarily
    
    Args:
        upload_file: FastAPI upload file object
        
    Returns:
        Path to saved file
    """
    try:
        # Create unique filename
        file_path = os.path.join(settings.UPLOAD_DIR, upload_file.filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        return file_path
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


@app.post("/analyze", response_model=ResumeAnalysisResponse, tags=["Analysis"])
async def analyze_resume(
    file: UploadFile = File(..., description="Resume file (PDF, DOCX, or TXT)")
):
    """
    Analyze uploaded resume and extract structured insights
    
    **Process:**
    1. Extract text from resume
    2. Preprocess and clean text
    3. Analyze using Google Gemini AI
    4. Return structured results with skill scores
    
    **Returns:**
    - skills: List of extracted skills with confidence scores (1-10)
    - experience: Estimated years of experience
    - tech_stack: Categorized technologies
    - summary: Professional summary
    """
    file_path = None
    
    try:
        # Validate Gemini is configured
        if not gemini_analyzer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini AI service not configured. Please set GOOGLE_API_KEY."
            )
        
        # Validate file
        validate_file(file)
        
        # Save uploaded file
        file_path = await save_upload_file(file)
        
        # Step 1: Extract text
        print(f"📄 Extracting text from: {file.filename}")
        raw_text = TextExtractor.extract(file_path)
        
        if not raw_text or len(raw_text.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient text content in resume"
            )
        
        # Step 2: Preprocess text
        print("🧹 Preprocessing text...")
        cleaned_text = TextPreprocessor.preprocess(raw_text)
        text_stats = TextPreprocessor.get_text_statistics(cleaned_text)
        
        # Step 3: Analyze with Gemini
        print("🤖 Analyzing with Gemini AI...")
        analysis_result = gemini_analyzer.analyze_resume(cleaned_text)
        
        # Step 4: Structure response
        skills_list = [
            Skill(**skill) for skill in analysis_result.get('skills', [])
        ]
        
        # Rank skills by score (highest to lowest)
        skills_list.sort(key=lambda x: x.score, reverse=True)
        
        experience_data = analysis_result.get('experience', {})
        experience_info = ExperienceInfo(**experience_data) if experience_data else None
        
        tech_stack_data = analysis_result.get('tech_stack', {})
        tech_stack = TechStack(**tech_stack_data)
        
        response = ResumeAnalysisResponse(
            status="success",
            skills=skills_list,
            experience=experience_info,
            tech_stack=tech_stack,
            summary=analysis_result.get('summary', ''),
            raw_text_length=len(raw_text),
            message=f"Successfully analyzed resume with {len(skills_list)} skills identified"
        )
        
        print(f"✅ Analysis complete: {len(skills_list)} skills found")
        if skills_list:
            print(f"🏆 Top skill: {skills_list[0].name} (Score: {skills_list[0].score}/10)")
        
        return response
        
    except HTTPException:
        raise
        
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
    
    finally:
        # Cleanup: Remove uploaded file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Warning: Failed to cleanup file: {str(e)}")


@app.post("/extract-text", tags=["Utility"])
async def extract_text_only(
    file: UploadFile = File(..., description="Resume file (PDF, DOCX, or TXT)")
):
    """
    Extract raw text from resume without AI analysis
    
    Useful for debugging or previewing text extraction
    """
    file_path = None
    
    try:
        validate_file(file)
        file_path = await save_upload_file(file)
        
        raw_text = TextExtractor.extract(file_path)
        cleaned_text = TextPreprocessor.preprocess(raw_text)
        stats = TextPreprocessor.get_text_statistics(cleaned_text)
        
        return {
            "status": "success",
            "filename": file.filename,
            "raw_text": raw_text[:1000] + "..." if len(raw_text) > 1000 else raw_text,
            "cleaned_text": cleaned_text[:1000] + "..." if len(cleaned_text) > 1000 else cleaned_text,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text extraction failed: {str(e)}"
        )
    
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


@app.get("/analyze/github/{username}", tags=["GitHub Analysis"])
async def analyze_github_profile(username: str):
    """
    Analyze a GitHub user's profile to extract skills, experience, and project insights
    
    **Process:**
    1. Fetch GitHub user profile and repositories
    2. Aggregate language statistics and project data
    3. Analyze using Google Gemini AI for skill scoring
    4. Return structured insights with experience level
    
    **Parameters:**
    - username: GitHub username (e.g., "tulika-anand")
    
    **Returns:**
    - User profile information
    - Repository statistics (languages, stars, forks)
    - AI-powered skill analysis with scores (1-10)
    - Experience level assessment
    - Notable projects with complexity scores
    - Dominant domains (AI/ML, Web Dev, etc.)
    """
    try:
        # Validate Gemini is configured
        if not gemini_analyzer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini AI service not configured. Please set GOOGLE_API_KEY."
            )
        
        # Step 1: Fetch GitHub data
        print(f"🔍 Fetching GitHub data for: {username}")
        fetcher = GitHubFetcher(access_token=os.getenv("GITHUB_TOKEN"))
        user_data, repo_data = await fetcher.get_user_and_repos(username)
        
        if not repo_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No public repositories found for user '{username}'"
            )
        
        # Step 2: Aggregate data
        print("📊 Aggregating repository statistics...")
        summary = fetcher.summarize_data(user_data, repo_data)
        
        # Step 3: Analyze with Gemini
        print("🤖 Analyzing profile with Gemini AI...")
        analyzer = GitHubProfileAnalyzer()
        analysis = analyzer.analyze_profile(summary)
        
        # Step 4: Build response
        response = {
            "status": "success",
            "username": username,
            "github_url": user_data["html_url"],
            "user_info": summary["user"],
            "stats": summary["stats"],
            "top_repositories": summary["repositories"][:5],  # Top 5 repos
            "analysis": analysis,
            "message": f"Successfully analyzed GitHub profile for {username}"
        }
        
        print(f"✅ GitHub analysis complete")
        print(f"🏆 Experience Level: {analysis.get('overall_experience_level', 'Unknown')}")
        
        return response
        
    except ValueError as e:
        # Handle expected errors (user not found, rate limit, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ GitHub analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub analysis failed: {str(e)}"
        )


@app.post("/analyze/combined", tags=["Combined Analysis"])
async def analyze_resume_and_github(
    file: UploadFile = File(..., description="Resume file"),
    github_username: Optional[str] = None
):
    """
    Combined analysis: Resume + GitHub profile (if username provided)
    
    **Process:**
    1. Analyze resume file
    2. If GitHub username provided, analyze GitHub profile
    3. Return combined insights
    
    **Use Case:**
    - Complete candidate assessment
    - Cross-validate skills between resume and GitHub
    - Comprehensive technical profile
    """
    file_path = None
    
    try:
        if not gemini_analyzer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini AI service not configured"
            )
        
        # Analyze resume
        print(f"📄 Analyzing resume: {file.filename}")
        validate_file(file)
        file_path = await save_upload_file(file)
        
        raw_text = TextExtractor.extract(file_path)
        if not raw_text or len(raw_text.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient text content in resume"
            )
        
        cleaned_text = TextPreprocessor.preprocess(raw_text)
        resume_analysis = gemini_analyzer.analyze_resume(cleaned_text)
        
        # Build resume response
        skills_list = [Skill(**skill) for skill in resume_analysis.get('skills', [])]
        skills_list.sort(key=lambda x: x.score, reverse=True)
        
        resume_data = {
            "skills": [skill.dict() for skill in skills_list],
            "experience": resume_analysis.get('experience'),
            "tech_stack": resume_analysis.get('tech_stack'),
            "summary": resume_analysis.get('summary')
        }
        
        result = {
            "status": "success",
            "resume_analysis": resume_data
        }
        
        # Optionally analyze GitHub
        if github_username:
            print(f"🔍 Additionally analyzing GitHub: {github_username}")
            try:
                fetcher = GitHubFetcher()
                user_data, repo_data = await fetcher.get_user_and_repos(github_username)
                summary = fetcher.summarize_data(user_data, repo_data)
                
                github_analyzer_instance = GitHubProfileAnalyzer()
                github_analysis = github_analyzer_instance.analyze_profile(summary)
                
                result["github_analysis"] = {
                    "username": github_username,
                    "stats": summary["stats"],
                    "analysis": github_analysis
                }
                
                print("✅ Combined analysis complete")
            except Exception as gh_error:
                result["github_analysis"] = {
                    "status": "error",
                    "message": f"GitHub analysis failed: {str(gh_error)}"
                }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Combined analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Resume Intelligence Analyzer")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
