"""
Integrations package for Justice Agent tools.
Contains clients and interfaces for external services.
"""

from .web_justice_client import WebJusticeClient, WebJusticeAPIError, create_client

__all__ = [
    'WebJusticeClient',
    'WebJusticeAPIError', 
    'create_client'
]