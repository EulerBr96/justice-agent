"""
Process number validator for Brazilian CNJ format.
Handles extraction, validation, and formatting of legal process numbers.
"""

import re
import logging
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)


class ProcessValidationError(Exception):
    """Raised when process number validation fails."""
    pass


class ProcessValidator:
    """
    Validator for Brazilian legal process numbers following CNJ standard.
    CNJ Format: NNNNNNN-DD.AAAA.J.TR.OOOO
    Where:
    - NNNNNNN: Sequential number (7 digits)
    - DD: Verification digits (2 digits) 
    - AAAA: Year of registration (4 digits)
    - J: Judicial segment (1 digit)
    - TR: Court (2 digits)
    - OOOO: Origin (4 digits)
    """
    
    # CNJ format regex patterns
    CNJ_FULL_PATTERN = re.compile(r'(\d{7})-?(\d{2})\.?(\d{4})\.?(\d)\.?(\d{2})\.?(\d{4})')
    CNJ_LOOSE_PATTERN = re.compile(r'(\d{7,})[-.]?(\d{2})[-.]?(\d{4})[-.]?(\d)[-.]?(\d{2})[-.]?(\d{4})')
    
    # Alternative patterns for various formats
    ALTERNATIVE_PATTERNS = [
        re.compile(r'(\d{7})\s*-?\s*(\d{2})\s*\.?\s*(\d{4})\s*\.?\s*(\d)\s*\.?\s*(\d{2})\s*\.?\s*(\d{4})'),
        re.compile(r'(\d{20})'),  # 20 consecutive digits
    ]
    
    # Validation ranges
    VALID_YEARS = range(1998, 2050)  # CNJ system started in 1998
    VALID_SEGMENTS = [1, 2, 3, 4, 6, 8, 9]  # Valid judicial segments
    
    def __init__(self):
        """Initialize the process validator."""
        pass
    
    def extract_process_numbers(self, text: str) -> List[str]:
        """
        Extract all potential process numbers from text.
        
        Args:
            text: Text to search for process numbers
            
        Returns:
            List of potential process numbers found in the text
        """
        process_numbers = []
        text = str(text).strip()
        
        # Try main CNJ pattern first
        matches = self.CNJ_FULL_PATTERN.findall(text)
        for match in matches:
            formatted = self._format_process_parts(match)
            if formatted:
                process_numbers.append(formatted)
        
        # Try loose pattern for numbers with missing separators
        if not process_numbers:
            matches = self.CNJ_LOOSE_PATTERN.findall(text)
            for match in matches:
                formatted = self._format_process_parts(match)
                if formatted:
                    process_numbers.append(formatted)
        
        # Try alternative patterns
        if not process_numbers:
            for pattern in self.ALTERNATIVE_PATTERNS:
                matches = pattern.findall(text)
                for match in matches:
                    if isinstance(match, str) and len(match) == 20:
                        # 20-digit format: break into CNJ parts
                        parts = (
                            match[0:7],   # NNNNNNN
                            match[7:9],   # DD
                            match[9:13],  # AAAA
                            match[13:14], # J
                            match[14:16], # TR
                            match[16:20]  # OOOO
                        )
                        formatted = self._format_process_parts(parts)
                        if formatted:
                            process_numbers.append(formatted)
        
        # Remove duplicates while preserving order
        unique_processes = []
        seen = set()
        for proc in process_numbers:
            if proc not in seen:
                unique_processes.append(proc)
                seen.add(proc)
        
        logger.info(f"Extracted {len(unique_processes)} process numbers from text")
        return unique_processes
    
    def _format_process_parts(self, parts: Tuple[str, ...]) -> Optional[str]:
        """
        Format process number parts into standard CNJ format.
        
        Args:
            parts: Tuple of process number parts
            
        Returns:
            Formatted process number or None if invalid
        """
        if len(parts) != 6:
            return None
        
        sequential, check_digits, year, segment, court, origin = parts
        
        # Ensure correct lengths
        sequential = sequential.zfill(7)
        check_digits = check_digits.zfill(2)
        year = year.zfill(4)
        segment = segment.zfill(1)
        court = court.zfill(2)
        origin = origin.zfill(4)
        
        # Basic validation
        try:
            year_int = int(year)
            segment_int = int(segment)
            
            if year_int not in self.VALID_YEARS:
                logger.debug(f"Invalid year: {year}")
                return None
            
            if segment_int not in self.VALID_SEGMENTS:
                logger.debug(f"Invalid segment: {segment}")
                return None
                
        except ValueError:
            logger.debug(f"Invalid numeric parts in process number")
            return None
        
        # Format as standard CNJ format
        formatted = f"{sequential}-{check_digits}.{year}.{segment}.{court}.{origin}"
        return formatted
    
    def validate_process_number(self, process_number: str) -> bool:
        """
        Validate a process number according to CNJ rules.
        
        Args:
            process_number: Process number to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Extract and reformat to ensure consistency
            extracted = self.extract_process_numbers(process_number)
            if not extracted:
                return False
            
            # Additional validation could include check digit verification
            # For now, we rely on format validation
            return len(extracted) == 1
            
        except Exception as e:
            logger.debug(f"Validation failed for {process_number}: {str(e)}")
            return False
    
    def normalize_process_number(self, process_number: str) -> str:
        """
        Normalize a process number to standard CNJ format.
        
        Args:
            process_number: Process number to normalize
            
        Returns:
            Normalized process number
            
        Raises:
            ProcessValidationError: If process number is invalid
        """
        extracted = self.extract_process_numbers(process_number)
        
        if not extracted:
            raise ProcessValidationError(f"No valid process number found in: {process_number}")
        
        if len(extracted) > 1:
            logger.warning(f"Multiple process numbers found, using first: {extracted[0]}")
        
        return extracted[0]
    
    def extract_first_valid_process(self, text: str) -> Optional[str]:
        """
        Extract the first valid process number from text.
        
        Args:
            text: Text to search
            
        Returns:
            First valid process number or None if none found
        """
        extracted = self.extract_process_numbers(text)
        return extracted[0] if extracted else None


# Module-level convenience functions
_validator = ProcessValidator()

def extract_process_numbers(text: str) -> List[str]:
    """Extract process numbers from text."""
    return _validator.extract_process_numbers(text)

def validate_process_number(process_number: str) -> bool:
    """Validate a process number."""
    return _validator.validate_process_number(process_number)

def normalize_process_number(process_number: str) -> str:
    """Normalize a process number to standard format."""
    return _validator.normalize_process_number(process_number)

def extract_first_process(text: str) -> Optional[str]:
    """Extract the first valid process number from text."""
    return _validator.extract_first_valid_process(text)