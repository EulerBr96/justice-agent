"""
Utilities package for Justice Agent tools.
Provides shared functionality for process and document validation, polling, and configuration.
"""

from .process_validator import (
    extract_process_numbers,
    validate_process_number,
    normalize_process_number,
    extract_first_process,
    ProcessValidator,
    ProcessValidationError
)

from .document_validator import (
    extract_documents,
    validate_cpf,
    validate_cnpj,
    identify_document_type,
    normalize_document,
    extract_first_document,
    get_clean_document,
    DocumentValidator,
    DocumentValidationError
)

from .polling_manager import (
    PollingManager,
    PollingConfig,
    PollingTimeoutError,
    poll_search_completion,
    create_progress_logger
)

__all__ = [
    # Process validation
    'extract_process_numbers',
    'validate_process_number', 
    'normalize_process_number',
    'extract_first_process',
    'ProcessValidator',
    'ProcessValidationError',
    
    # Document validation
    'extract_documents',
    'validate_cpf',
    'validate_cnpj',
    'identify_document_type',
    'normalize_document',
    'extract_first_document',
    'get_clean_document',
    'DocumentValidator',
    'DocumentValidationError',
    
    # Polling management
    'PollingManager',
    'PollingConfig',
    'PollingTimeoutError', 
    'poll_search_completion',
    'create_progress_logger'
]