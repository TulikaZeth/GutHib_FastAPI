"""
Pydantic models for GitHub analysis
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class GitHubUser(BaseModel):
    """GitHub user profile information"""
    username: str
    name: str
    bio: str
    location: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    blog: Optional[str] = None
    twitter: Optional[str] = None
    followers: int
    following: int
    public_repos: int
    created_at: str
    profile_url: str


class RepositorySummary(BaseModel):
    """Individual repository summary"""
    name: str
    description: str
    language: str
    stars: int
    forks: int
    topics: List[str]
    url: str


class NotableProject(BaseModel):
    """Notable project analysis"""
    name: str
    description: str
    complexity_score: int = Field(..., ge=1, le=10)
    impact_score: int = Field(..., ge=1, le=10)
    technologies: List[str]
    stars: int


class ProjectAnalysis(BaseModel):
    """Project analysis summary"""
    total_analyzed: int
    notable_projects: List[NotableProject]
    project_domains: List[str]


class ActivityAssessment(BaseModel):
    """Activity and engagement assessment"""
    consistency: str
    community_engagement: str
    code_quality_indicators: str


class DominantTechStack(BaseModel):
    """Categorized technology stack"""
    languages: List[str]
    frameworks: List[str]
    tools: List[str]
    domains: List[str]


class GitHubAnalysisResponse(BaseModel):
    """Complete GitHub profile analysis response"""
    status: str = "success"
    username: str
    github_url: str
    
    # User info
    user_info: GitHubUser
    
    # Statistics
    stats: Dict[str, Any]
    
    # AI Analysis
    analysis: Dict[str, Any]
    
    message: Optional[str] = None


class GitHubAnalysisError(BaseModel):
    """Error response for GitHub analysis"""
    status: str = "error"
    message: str
    details: Optional[str] = None
