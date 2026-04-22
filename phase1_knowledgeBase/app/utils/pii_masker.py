"""
PII Masking Utility
Replaces personally identifiable information with [REDACTED] tokens.
Also detects and blocks queries that request PII.
"""
import re
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Keywords that indicate a user is requesting PII (asking for SOMEONE'S personal info)
# These patterns look for: request verb + PII type + possession indicator (of/for/person's)
PII_REQUEST_PATTERNS = [
    # Email requests for specific person
    r"\b(?:give|send|share|tell|provide|get|find|look up|search for).*\bemail\b.*\b(?:of|for)\b",
    r"\b(?:ceo|manager|director|contact|person|someone|him|her|their).*\bemail\b",
    r"\bemail\b.*\b(?:of|for|ceo|manager|director|contact|person)\b",
    # Phone requests for specific person
    r"\b(?:give|send|share|tell|provide|get|find|look up|search for).*\b(?:phone|mobile|contact number)\b.*\b(?:of|for)\b",
    r"\b(?:phone|mobile|contact number).*\b(?:of|for|ceo|manager|director|person)\b",
    # Address/Location requests for specific person
    r"\b(?:home address|residence|where does.*live|personal address)\b.*\b(?:of|for)\b",
    # Name requests for specific people
    r"\b(?:full name|real name|personal details|contact info)\b.*\b(?:of|for)\b",
    # PAN/Aadhaar/Account requests for specific person - MUST have "of" or "for" or person's name
    r"\b(?:give|send|share|tell|provide|get|find|look up|search for).*(?:pan|aadhaar|account number|account id|client id).*\b(?:of|for)\b",
    r"\b(?:pan|aadhaar|account number|account id|client id).*\b(?:of|for|ceo|manager|director|person|someone|him|her)\b",
    r"\b(?:his|her|their)\b.*\b(?:pan|aadhaar|account number|email|phone|mobile)\b",
]

class PIIMasker:
    """
    Masks PII in text to comply with technical constraints.
    Replaces: Names, Phone numbers, Email addresses, Account numbers
    Also detects queries that request PII and blocks them.
    """
    
    def __init__(self):
        self.redaction_token = "[REDACTED]"
        self.patterns = self._compile_patterns()
        self.pii_request_patterns = [re.compile(p, re.IGNORECASE) for p in PII_REQUEST_PATTERNS]
    
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
    
    def detect_pii_request(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detect and block ALL queries about sensitive personal identifiers.
        
        This blocks:
        1. PII requests (asking for someone's personal info):
           - "What is the PAN of the CEO?"
           - "Give me the email of the manager"
        2. ALL general queries about sensitive IDs:
           - "What is PAN?" (blocked - not relevant to mutual funds)
           - "Tell me about Aadhaar" (blocked - not relevant to mutual funds)
        
        Args:
            text: Input query text
            
        Returns:
            Tuple of (is_blocked, reason)
            - is_blocked: True if query should be blocked
            - reason: Description of why blocked, or None
        """
        if not text:
            return False, None
        
        text_lower = text.lower()
        
        # BLOCK ALL queries about sensitive government IDs (PAN, Aadhaar)
        # These are not relevant to mutual fund information
        blocked_id_keywords = ["pan", "aadhaar", "aadhar", "uid"]
        for keyword in blocked_id_keywords:
            # Match as whole word only (avoid matching "pan" inside "span")
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, text_lower):
                logger.warning(f"Blocked query containing restricted ID term: {keyword}")
                return True, f"Queries about {keyword.upper()} are not supported. I can help with mutual fund information only."
        
        # Check against PII request patterns (email, phone, account numbers of specific people)
        for pattern in self.pii_request_patterns:
            if pattern.search(text):
                matched = pattern.search(text).group(0)
                logger.warning(f"PII request detected: {matched}")
                return True, f"Request for personal information detected: '{matched}'"
        
        return False, None
    
    def get_pii_refusal_message(self, reason: str) -> str:
        """
        Get a refusal message when PII is requested.
        
        Args:
            reason: The reason for refusal
            
        Returns:
            Refusal message for the user
        """
        return f"""I cannot provide personal information such as email addresses, phone numbers, or other private details. 

I can help you with:
• Fund facts and documentation
• Fee structures and expense ratios
• Exit loads and investment rules
• General mutual fund information

For specific contact details, please visit the official HDFC Mutual Fund website or contact their customer service directly.

Last updated from sources: {self.redaction_token}"""
