"""
Justice Agent Tools Package.
AI Agent tools for consulting legal processes via the Web Justice API.
"""

from .process_consultation import consult_process, ProcessConsultationTool, consult_legal_process_tool
from .hybrid_process_search import HybridProcessSearchTool, hybrid_process_search
from .config import get_config, set_config, ToolsConfig, ENV_VARS_HELP

__version__ = "1.0.0"

__all__ = [
    # Main functions
    'consult_process',
    
    # Tool classes
    'ProcessConsultationTool',
    'HybridProcessSearchTool',
    
    # Agno tools  
    'consult_legal_process_tool',
    'hybrid_process_search',
    
    # Configuration
    'get_config',
    'set_config',
    'ToolsConfig',
    'ENV_VARS_HELP',
]