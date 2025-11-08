"""
Text preprocessing layer - Clean and normalize extracted text
"""
import re
from typing import List


class TextPreprocessor:
    """Preprocess and clean resume text"""
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Remove extra whitespace while preserving structure"""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        # Replace multiple newlines with double newline (paragraph breaks)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines)
    
    @staticmethod
    def remove_special_characters(text: str, preserve_basic: bool = True) -> str:
        """
        Remove special characters while preserving basic punctuation
        
        Args:
            text: Input text
            preserve_basic: If True, keep basic punctuation like .,;:-()
        """
        if preserve_basic:
            # Keep alphanumeric, spaces, and basic punctuation
            text = re.sub(r'[^a-zA-Z0-9\s.,;:()\-+#/\n]', '', text)
        else:
            # Keep only alphanumeric and spaces
            text = re.sub(r'[^a-zA-Z0-9\s\n]', '', text)
        
        return text
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text without losing too much context
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        # Convert to lowercase for consistency in analysis
        # Note: We keep the original case for Gemini as it helps with proper noun recognition
        return text
    
    @staticmethod
    def extract_sections(text: str) -> dict:
        """
        Attempt to identify common resume sections
        
        Returns:
            Dictionary with identified sections
        """
        sections = {
            'skills': '',
            'experience': '',
            'education': '',
            'projects': '',
            'other': ''
        }
        
        # Common section headers
        section_patterns = {
            'skills': r'(?i)(skills|technical\s+skills|core\s+competencies)',
            'experience': r'(?i)(experience|work\s+experience|employment|professional\s+experience)',
            'education': r'(?i)(education|academic|qualification)',
            'projects': r'(?i)(projects|portfolio)'
        }
        
        # This is a simplified section extraction
        # In production, you might want more sophisticated parsing
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text)
            if match:
                sections[section_name] = text[match.start():]
        
        return sections
    
    @classmethod
    def preprocess(cls, text: str, aggressive: bool = False) -> str:
        """
        Complete preprocessing pipeline
        
        Args:
            text: Raw extracted text
            aggressive: If True, apply more aggressive cleaning
            
        Returns:
            Preprocessed text
        """
        if not text or not text.strip():
            raise ValueError("Empty text provided for preprocessing")
        
        # Remove extra whitespace
        text = cls.remove_extra_whitespace(text)
        
        # Remove special characters (but preserve basic structure)
        text = cls.remove_special_characters(text, preserve_basic=not aggressive)
        
        # Final cleanup
        text = text.strip()
        
        if not text:
            raise ValueError("Text became empty after preprocessing")
        
        return text
    
    @staticmethod
    def get_text_statistics(text: str) -> dict:
        """Get basic statistics about the text"""
        words = text.split()
        lines = text.split('\n')
        
        return {
            'total_characters': len(text),
            'total_words': len(words),
            'total_lines': len(lines),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0
        }
