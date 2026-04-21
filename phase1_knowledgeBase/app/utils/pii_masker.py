"""
PII Masking Utility
Replaces personally identifiable information with [REDACTED] tokens.
"""
import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class PIIMasker:
    """
    Masks PII in text to comply with technical constraints.
    Replaces: Names, Phone numbers, Email addresses, Account numbers
    """
    
    def __init__(self):
        self.redaction_token = "[REDACTED]"
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for PII detection."""
        return {
            # Email addresses
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            
            # Phone numbers (Indian format)
            "phone": re.compile(r'\b(?:\+91|0)?[6789]\d{9}\b'),
            
            # Account numbers (10-20 digits)
            "account": re.compile(r'\b\d{10,20}\b'),
            
            # PAN numbers (Indian tax ID)
            "pan": re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'),
            
            # Aadhaar (12 digits, often with spaces)
            "aadhaar": re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b'),
            
            # Names (simple heuristic - capitalized words that could be names)
            # This is a basic implementation - production would use NER
            "name": re.compile(r'\b(?:Mr|Mrs|Ms|Dr|Shri|Smt)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'),
        }
    
    def mask(self, text: str) -> str:
        """
        Mask PII in text.
        
        Args:
            text: Input text that may contain PII
            
        Returns:
            Text with PII replaced by [REDACTED]
        """
        if not text:
            return text
        
        masked = text
        
        # Apply each pattern
        for pii_type, pattern in self.patterns.items():
            masked = pattern.sub(self.redaction_token, masked)
        
        return masked
    
    def mask_entities(self, text: str) -> tuple[str, List[Dict]]:
        """
        Mask PII and return list of masked entities.
        
        Args:
            text: Input text
            
        Returns:
            (masked_text, list of entities with type and position)
        """
        if not text:
            return text, []
        
        masked = text
        entities = []
        
        for pii_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                entities.append({
                    "type": pii_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
            
            masked = pattern.sub(self.redaction_token, masked)
        
        return masked, entities
    
    def detect_pii(self, text: str) -> bool:
        """
        Check if text contains PII.
        
        Args:
            text: Input text
            
        Returns:
            True if PII detected, False otherwise
        """
        if not text:
            return False
        
        for pattern in self.patterns.values():
            if pattern.search(text):
                return True
        
        return False
