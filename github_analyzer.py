"""
GitHub Profile Analyzer using Gemini AI
"""
import json
import logging
import google.generativeai as genai
from typing import Dict, Any
from config import settings

logger = logging.getLogger(__name__)


class GitHubProfileAnalyzer:
    """Analyze GitHub profile using Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini analyzer"""
        if not settings.GOOGLE_API_KEY:
            raise ValueError("Google API key not configured")
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def create_analysis_prompt(self, summary: Dict[str, Any]) -> str:
        """
        Create prompt for GitHub profile analysis
        
        Args:
            summary: Aggregated GitHub profile data
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are an expert Technical Recruiter analyzing a GitHub profile. Provide a structured assessment.

GITHUB PROFILE DATA:
{json.dumps(summary, indent=2)}

Analyze this GitHub profile and return a JSON response with this EXACT structure:

{{
  "overall_experience_level": "Beginner|Intermediate|Advanced|Expert",
  "experience_years_estimate": 0.0,
  "skills_with_scores": {{
    "language_name": 1-10
  }},
  "dominant_tech_stack": {{
    "languages": ["Python", "JavaScript"],
    "frameworks": ["React", "FastAPI"],
    "tools": ["Docker", "Git"],
    "domains": ["AI/ML", "Web Development"]
  }},
  "project_analysis": {{
    "total_analyzed": 0,
    "notable_projects": [
      {{
        "name": "project_name",
        "description": "brief description",
        "complexity_score": 1-10,
        "impact_score": 1-10,
        "technologies": ["tech1", "tech2"],
        "stars": 0
      }}
    ],
    "project_domains": ["AI/ML", "Web Dev", "Data Science"]
  }},
  "activity_assessment": {{
    "consistency": "Low|Medium|High",
    "community_engagement": "Low|Medium|High",
    "code_quality_indicators": "Stars and forks suggest quality level"
  }},
  "strengths": ["strength1", "strength2"],
  "areas_for_growth": ["area1", "area2"],
  "professional_summary": "2-3 sentence summary of technical profile"
}}

SCORING GUIDE:
- Skills (1-10): Based on frequency, project complexity, recent activity
- Complexity (1-10): 1=basic, 5=moderate, 10=highly complex
- Impact (1-10): Based on stars, forks, description

Experience Level:
- Beginner: <1 year, basic projects
- Intermediate: 1-3 years, moderate complexity
- Advanced: 3-5 years, complex projects, good engagement
- Expert: 5+ years, highly complex projects, strong community presence

CRITICAL: Return ONLY valid JSON. No markdown, no explanations."""
        
        return prompt
    
    def analyze_profile(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze GitHub profile using Gemini
        
        Args:
            summary: Aggregated GitHub data
            
        Returns:
            Structured analysis
        """
        try:
            logger.info("Analyzing GitHub profile with Gemini...")
            
            prompt = self.create_analysis_prompt(summary)
            
            # Generate analysis with JSON mode
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
            )
            
            try:
                generation_config.response_mime_type = "application/json"
            except:
                pass
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            logger.info(f"Received analysis response ({len(response.text)} chars)")
            
            # Parse response
            analysis = self.parse_response(response.text)
            
            return analysis
            
        except Exception as e:
            logger.error(f"GitHub profile analysis failed: {str(e)}")
            raise RuntimeError(f"Analysis failed: {str(e)}")
    
    def parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse and validate Gemini's response
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Parsed JSON
        """
        try:
            # Clean response
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Extract JSON object
            start_idx = cleaned_text.find('{')
            end_idx = cleaned_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                cleaned_text = cleaned_text[start_idx:end_idx + 1]
            
            # Parse JSON
            parsed = json.loads(cleaned_text)
            
            logger.info("Successfully parsed GitHub analysis response")
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            logger.error(f"Response preview: {response_text[:500]}...")
            raise ValueError(f"Failed to parse analysis response: {str(e)}")
