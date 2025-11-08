"""
Configuration management for Resume Intelligence Analyzer
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # API Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".doc", ".txt"}
    UPLOAD_DIR: str = "uploads"
    
    # Gemini Configuration
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2048
    
    def validate(self):
        """Validate required settings"""
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in .env file")
        
        # Create upload directory if it doesn't exist
        if not os.path.exists(self.UPLOAD_DIR):
            os.makedirs(self.UPLOAD_DIR)

settings = Settings()
