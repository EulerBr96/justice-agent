"""
Document validator for Brazilian CPF and CNPJ formats.
Handles extraction, validation, and formatting of legal documents.
"""

import re
import logging
from typing import Optional, List, Union

logger = logging.getLogger(__name__)


class DocumentValidationError(Exception):
    """Raised when document validation fails."""
    pass


class DocumentValidator:
    """
    Validator for Brazilian legal documents (CPF and CNPJ).
    """
    
    # CPF patterns (11 digits)
    CPF_PATTERN = re.compile(r'(\d{3})\.?(\d{3})\.?(\d{3})-?(\d{2})')
    CPF_NUMBERS_ONLY = re.compile(r'(\d{11})')
    
    # CNPJ patterns (14 digits) 
    CNPJ_PATTERN = re.compile(r'(\d{2})\.?(\d{3})\.?(\d{3})/?(\d{4})-?(\d{2})')
    CNPJ_NUMBERS_ONLY = re.compile(r'(\d{14})')
    
    # Combined pattern for any document
    DOCUMENT_PATTERN = re.compile(r'\b\d{11,14}\b|\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b|\b\d{2}\.?\d{3}\.?\d{3}/?0001-?\d{2}\b')
    
    def __init__(self):
        """Initialize the document validator."""
        pass
    
    def extract_documents(self, text: str) -> List[str]:
        """
        Extract all potential CPF/CNPJ numbers from text.
        
        Args:
            text: Text to search for documents
            
        Returns:
            List of potential documents found in the text
        """
        documents = []
        text = str(text).strip()
        
        # Look for CPF patterns
        cpf_matches = self.CPF_PATTERN.findall(text)
        for match in cpf_matches:
            if len(match) == 4:  # (xxx, xxx, xxx, xx)
                cpf = ''.join(match)
                if self._is_valid_cpf_length(cpf):
                    formatted = self._format_cpf(cpf)
                    if formatted and self.validate_cpf(formatted):
                        documents.append(formatted)
        
        # Look for CNPJ patterns
        cnpj_matches = self.CNPJ_PATTERN.findall(text)
        for match in cnpj_matches:
            if len(match) == 5:  # (xx, xxx, xxx, xxxx, xx)
                cnpj = ''.join(match)
                if self._is_valid_cnpj_length(cnpj):
                    formatted = self._format_cnpj(cnpj)
                    if formatted and self.validate_cnpj(formatted):
                        documents.append(formatted)
        
        # Look for numbers-only patterns
        numbers = re.findall(r'\b\d{11,14}\b', text)
        for number in numbers:
            if len(number) == 11 and self.validate_cpf(number):
                formatted = self._format_cpf(number)
                if formatted not in documents:
                    documents.append(formatted)
            elif len(number) == 14 and self.validate_cnpj(number):
                formatted = self._format_cnpj(number)
                if formatted not in documents:
                    documents.append(formatted)
        
        # Remove duplicates while preserving order
        unique_docs = []
        seen = set()
        for doc in documents:
            clean_doc = re.sub(r'[^\d]', '', doc)  # Remove formatting for comparison
            if clean_doc not in seen:
                unique_docs.append(doc)
                seen.add(clean_doc)
        
        logger.info(f"Extracted {len(unique_docs)} documents from text")
        return unique_docs
    
    def _is_valid_cpf_length(self, cpf: str) -> bool:
        """Check if CPF has correct length."""
        clean_cpf = re.sub(r'[^\d]', '', cpf)
        return len(clean_cpf) == 11
    
    def _is_valid_cnpj_length(self, cnpj: str) -> bool:
        """Check if CNPJ has correct length."""
        clean_cnpj = re.sub(r'[^\d]', '', cnpj)
        return len(clean_cnpj) == 14
    
    def _format_cpf(self, cpf: str) -> Optional[str]:
        """Format CPF to standard format: XXX.XXX.XXX-XX"""
        clean_cpf = re.sub(r'[^\d]', '', cpf)
        if len(clean_cpf) != 11:
            return None
        return f"{clean_cpf[:3]}.{clean_cpf[3:6]}.{clean_cpf[6:9]}-{clean_cpf[9:11]}"
    
    def _format_cnpj(self, cnpj: str) -> Optional[str]:
        """Format CNPJ to standard format: XX.XXX.XXX/XXXX-XX"""
        clean_cnpj = re.sub(r'[^\d]', '', cnpj)
        if len(clean_cnpj) != 14:
            return None
        return f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:8]}/{clean_cnpj[8:12]}-{clean_cnpj[12:14]}"
    
    def validate_cpf(self, cpf: str) -> bool:
        """
        Validate CPF using the official algorithm.
        
        Args:
            cpf: CPF number to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Remove formatting
            clean_cpf = re.sub(r'[^\d]', '', cpf)
            
            # Check length
            if len(clean_cpf) != 11:
                return False
            
            # Check for invalid patterns (all same digits)
            if clean_cpf == clean_cpf[0] * 11:
                return False
            
            # Calculate first verification digit
            sum1 = sum(int(clean_cpf[i]) * (10 - i) for i in range(9))
            digit1 = ((sum1 * 10) % 11) % 10
            
            # Calculate second verification digit
            sum2 = sum(int(clean_cpf[i]) * (11 - i) for i in range(10))
            digit2 = ((sum2 * 10) % 11) % 10
            
            # Check if calculated digits match
            return digit1 == int(clean_cpf[9]) and digit2 == int(clean_cpf[10])
            
        except (ValueError, IndexError):
            return False
    
    def validate_cnpj(self, cnpj: str) -> bool:
        """
        Validate CNPJ using the official algorithm.
        
        Args:
            cnpj: CNPJ number to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Remove formatting
            clean_cnpj = re.sub(r'[^\d]', '', cnpj)
            
            # Check length
            if len(clean_cnpj) != 14:
                return False
            
            # Check for invalid patterns (all same digits)
            if clean_cnpj == clean_cnpj[0] * 14:
                return False
            
            # Calculate first verification digit
            weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            sum1 = sum(int(clean_cnpj[i]) * weights1[i] for i in range(12))
            digit1 = 11 - (sum1 % 11) if sum1 % 11 >= 2 else 0
            
            # Calculate second verification digit
            weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            sum2 = sum(int(clean_cnpj[i]) * weights2[i] for i in range(13))
            digit2 = 11 - (sum2 % 11) if sum2 % 11 >= 2 else 0
            
            # Check if calculated digits match
            return digit1 == int(clean_cnpj[12]) and digit2 == int(clean_cnpj[13])
            
        except (ValueError, IndexError):
            return False
    
    def identify_document_type(self, document: str) -> Optional[str]:
        """
        Identify if document is CPF or CNPJ.
        
        Args:
            document: Document string to identify
            
        Returns:
            'CPF', 'CNPJ', or None if invalid
        """
        clean_doc = re.sub(r'[^\d]', '', document)
        
        if len(clean_doc) == 11:
            return 'CPF' if self.validate_cpf(document) else None
        elif len(clean_doc) == 14:
            return 'CNPJ' if self.validate_cnpj(document) else None
        else:
            return None
    
    def normalize_document(self, document: str) -> str:
        """
        Normalize a document to standard format.
        
        Args:
            document: Document to normalize
            
        Returns:
            Normalized document
            
        Raises:
            DocumentValidationError: If document is invalid
        """
        doc_type = self.identify_document_type(document)
        
        if doc_type == 'CPF':
            formatted = self._format_cpf(document)
            if not formatted:
                raise DocumentValidationError(f"Invalid CPF format: {document}")
            return formatted
        elif doc_type == 'CNPJ':
            formatted = self._format_cnpj(document)
            if not formatted:
                raise DocumentValidationError(f"Invalid CNPJ format: {document}")
            return formatted
        else:
            raise DocumentValidationError(f"Invalid document: {document}")
    
    def extract_first_valid_document(self, text: str) -> Optional[str]:
        """
        Extract the first valid document from text.
        
        Args:
            text: Text to search
            
        Returns:
            First valid document or None if none found
        """
        extracted = self.extract_documents(text)
        return extracted[0] if extracted else None
    
    def get_clean_document(self, document: str) -> str:
        """
        Get document with only numbers (no formatting).
        
        Args:
            document: Formatted document
            
        Returns:
            Document with only numbers
        """
        return re.sub(r'[^\d]', '', document)


# Module-level convenience functions
_validator = DocumentValidator()

def extract_documents(text: str) -> List[str]:
    """Extract documents from text."""
    return _validator.extract_documents(text)

def validate_cpf(cpf: str) -> bool:
    """Validate a CPF."""
    return _validator.validate_cpf(cpf)

def validate_cnpj(cnpj: str) -> bool:
    """Validate a CNPJ."""
    return _validator.validate_cnpj(cnpj)

def identify_document_type(document: str) -> Optional[str]:
    """Identify document type."""
    return _validator.identify_document_type(document)

def normalize_document(document: str) -> str:
    """Normalize a document to standard format."""
    return _validator.normalize_document(document)

def extract_first_document(text: str) -> Optional[str]:
    """Extract the first valid document from text."""
    return _validator.extract_first_valid_document(text)

def get_clean_document(document: str) -> str:
    """Get document with only numbers."""
    return _validator.get_clean_document(document)