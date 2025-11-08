"""
Pydantic models for request/response validation
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Skill(BaseModel):
    """Individual skill with confidence score"""
    name: str = Field(..., description="Name of the skill/technology")
    score: int = Field(..., ge=1, le=10, description="Confidence score from 1-10")
    category: str = Field(..., description="Category: Language, Framework, Tool, or Library")
    description: Optional[str] = Field(None, description="Additional context about the skill usage")


class ExperienceInfo(BaseModel):
    """Experience duration information"""
    total_years: float = Field(..., description="Total years of experience")
    confidence: str = Field(..., description="Confidence level: high, medium, or low")
    source: str = Field(..., description="How the experience was determined")


class TechStack(BaseModel):
    """Categorized technology stack"""
    languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks and libraries")
    tools: List[str] = Field(default_factory=list, description="Development tools")
    libraries: List[str] = Field(default_factory=list, description="Specific libraries")
    databases: List[str] = Field(default_factory=list, description="Database systems")
    cloud_platforms: List[str] = Field(default_factory=list, description="Cloud platforms")


class ResumeAnalysisResponse(BaseModel):
    """Complete resume analysis response"""
    status: str = Field(..., description="Analysis status: success or error")
    skills: List[Skill] = Field(default_factory=list, description="Extracted skills with scores")
    experience: Optional[ExperienceInfo] = Field(None, description="Experience information")
    tech_stack: TechStack = Field(default_factory=TechStack, description="Categorized technologies")
    summary: str = Field(..., description="Brief professional summary")
    raw_text_length: int = Field(..., description="Length of extracted text")
    message: Optional[str] = Field(None, description="Additional information or error message")


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    message: str
    details: Optional[str] = None
