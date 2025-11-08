"""
AI Analysis Layer - Gemini integration for resume intelligence
"""
import json
import google.generativeai as genai
from typing import Dict, Any
from config import settings


class GeminiAnalyzer:
    """Analyze resume using Google Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini with API key"""
        if not settings.GOOGLE_API_KEY:
            raise ValueError("Google API key not configured")
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def create_analysis_prompt(self, resume_text: str) -> str:
        """
        Create a detailed prompt for Gemini to analyze the resume
        
        Args:
            resume_text: Preprocessed resume text
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert Resume Intelligence Analyst. Analyze the resume and return ONLY a valid JSON object.

RESUME TEXT:
{resume_text}

Return a JSON object with this EXACT structure (no markdown, no explanations, just pure JSON):

{{
  "skills": [
    {{
      "name": "skill name",
      "score": 1-10,
      "category": "Language|Framework|Tool|Library|Database|Cloud Platform",
      "description": "brief usage context"
    }}
  ],
  "experience": {{
    "total_years": 0.0,
    "confidence": "high|medium|low",
    "source": "how experience was determined"
  }},
  "tech_stack": {{
    "languages": [],
    "frameworks": [],
    "tools": [],
    "libraries": [],
    "databases": [],
    "cloud_platforms": []
  }},
  "summary": "2-3 sentence professional summary"
}}

SCORING GUIDE:
- 9-10: Very prominent, core expertise
- 6-8: Moderate frequency, practical experience
- 3-5: Mentioned 1-2 times
- 1-2: Briefly mentioned or inferred

CRITICAL: Return ONLY the JSON object. No markdown code blocks, no explanations, no additional text."""
        return prompt
    
    def parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse and validate Gemini's JSON response
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Parsed JSON dictionary
        """
        try:
            # Clean the response (remove markdown code blocks if present)
            cleaned_text = response_text.strip()
            
            # Remove ```json and ``` markers if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Try to find JSON object if there's extra text
            # Look for the first { and last }
            start_idx = cleaned_text.find('{')
            end_idx = cleaned_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                cleaned_text = cleaned_text[start_idx:end_idx + 1]
            
            # Parse JSON
            parsed_data = json.loads(cleaned_text)
            
            # Validate required fields
            required_fields = ['skills', 'experience', 'tech_stack', 'summary']
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = {} if field in ['experience', 'tech_stack'] else [] if field == 'skills' else ""
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            # Log the problematic response for debugging
            print(f"⚠️ Failed to parse JSON. Response preview: {response_text[:500]}...")
            raise ValueError(f"Failed to parse Gemini response as JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing Gemini response: {str(e)}")
    
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyze resume using Gemini
        
        Args:
            resume_text: Preprocessed resume text
            
        Returns:
            Structured analysis results
        """
        try:
            # Create prompt
            prompt = self.create_analysis_prompt(resume_text)
            
            # Generate response with JSON mode if supported
            generation_config = genai.types.GenerationConfig(
                temperature=settings.TEMPERATURE,
                max_output_tokens=settings.MAX_TOKENS,
            )
            
            # Try to use JSON mode for better formatting
            try:
                generation_config.response_mime_type = "application/json"
            except:
                pass  # Fallback if JSON mode not supported
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Parse response
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            print(f"📥 Received response from Gemini ({len(response.text)} chars)")
            
            analysis_result = self.parse_gemini_response(response.text)
            
            return analysis_result
            
        except Exception as e:
            raise RuntimeError(f"Gemini analysis failed: {str(e)}")
    
    def validate_skill_scores(self, skills: list) -> list:
        """
        Validate and normalize skill scores
        
        Args:
            skills: List of skill dictionaries
            
        Returns:
            Validated skills list
        """
        for skill in skills:
            if 'score' in skill:
                # Ensure score is between 1-10
                skill['score'] = max(1, min(10, int(skill['score'])))
            else:
                skill['score'] = 5  # Default medium score
        
        return skills
