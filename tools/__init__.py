"""
Justice Agent Tools Package.
AI Agent tools for consulting legal processes via the Web Justice API.
"""

from .process_consultation import consult_process, ProcessConsultationTool
from .document_consultation import consult_document, DocumentConsultationTool
from .config import get_config, set_config, ToolsConfig, ENV_VARS_HELP

__version__ = "1.0.0"

__all__ = [
    # Main functions
    'consult_process',
    'consult_document', 
    
    # Tool classes
    'ProcessConsultationTool',
    'DocumentConsultationTool',
    
    # Configuration
    'get_config',
    'set_config',
    'ToolsConfig',
    'ENV_VARS_HELP',
]