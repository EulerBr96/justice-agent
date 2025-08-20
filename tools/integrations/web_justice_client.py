"""
Web Justice API client for AI Agent tools.
Provides shared functionality for both process and document consultation tools.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urljoin

import httpx

logger = logging.getLogger(__name__)


class WebJusticeAPIError(Exception):
    """Custom exception for Web Justice API errors."""
    pass


class WebJusticeClient:
    """
    Client for interacting with Web Justice AI Agent API endpoints.
    Handles authentication, request/response processing, and error handling.
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the Web Justice API client.
        
        Args:
            base_url: API base URL (defaults to environment variable)
            api_key: API authentication key (defaults to environment variable)
        """
        self.base_url = base_url or os.getenv('WEB_JUSTICE_API_URL', 'http://localhost:8000')
        self.api_key = api_key or os.getenv('WEB_JUSTICE_API_KEY')
        
        if not self.api_key:
            raise ValueError("API key is required. Set WEB_JUSTICE_API_KEY environment variable.")
        
        # Remove trailing slash from base URL
        self.base_url = self.base_url.rstrip('/')
        
        # Setup HTTP client with default headers
        self.client = httpx.Client(
            headers={
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json',
                'User-Agent': 'AI-Agent-Tools/1.0'
            },
            timeout=30.0
        )
        
        logger.info(f"WebJusticeClient initialized with base URL: {self.base_url}")
    
    def initiate_search(self, document: str, search_type: str = "document") -> Dict[str, Any]:
        """
        Initiate a search for a document or process.
        
        Args:
            document: The document or process number to search for
            search_type: Either "document" or "process"
            
        Returns:
            Dict containing job_id and other search initiation details
            
        Raises:
            WebJusticeAPIError: If the API request fails
        """
        url = urljoin(self.base_url, '/api/ai-agent/initiate-search')
        
        payload = {
            "document": document,
            "search_type": search_type
        }
        
        try:
            logger.info(f"Initiating {search_type} search for: {document}")
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Search initiated successfully. Job ID: {data.get('job_id')}")
            return data
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"Search initiation failed: {error_msg}")
            raise WebJusticeAPIError(f"Failed to initiate search: {error_msg}")
        except httpx.RequestError as e:
            logger.error(f"Request failed: {str(e)}")
            raise WebJusticeAPIError(f"Request failed: {str(e)}")
    
    def get_search_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get detailed status of a search job.
        
        Args:
            job_id: The search job identifier
            
        Returns:
            Dict containing search status details
            
        Raises:
            WebJusticeAPIError: If the API request fails
        """
        url = urljoin(self.base_url, f'/api/searches/{job_id}/detailed-status')
        
        try:
            response = self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Job {job_id} status: {data.get('current_status')} - {data.get('progress_percentage', 0)}%")
            return data
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"Status check failed for job {job_id}: {error_msg}")
            raise WebJusticeAPIError(f"Failed to get status: {error_msg}")
        except httpx.RequestError as e:
            logger.error(f"Request failed: {str(e)}")
            raise WebJusticeAPIError(f"Request failed: {str(e)}")
    
    def get_processes(self, document: str) -> Dict[str, Any]:
        """
        Get the results of a completed search.
        
        Args:
            document: The document or process number that was searched
            
        Returns:
            Dict containing the list of processes found
            
        Raises:
            WebJusticeAPIError: If the API request fails or search is not complete
        """
        url = urljoin(self.base_url, f'/api/ai-agent/processos/{document}')
        
        try:
            logger.info(f"Retrieving results for: {document}")
            response = self.client.get(url)
            
            if response.status_code == 425:  # Too Early - search not complete
                error_data = response.json()
                logger.warning(f"Search not complete for {document}: {error_data}")
                raise WebJusticeAPIError(f"Search not complete: {error_data}")
            
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {data.get('total_processos', 0)} processes for {document}")
            return data
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"Failed to get results for {document}: {error_msg}")
            raise WebJusticeAPIError(f"Failed to get results: {error_msg}")
        except httpx.RequestError as e:
            logger.error(f"Request failed: {str(e)}")
            raise WebJusticeAPIError(f"Request failed: {str(e)}")
    
    def test_authentication(self) -> bool:
        """
        Test if the API key is valid.
        
        Returns:
            True if authentication is successful, False otherwise
        """
        url = urljoin(self.base_url, '/api/ai-agent/test-auth')
        
        try:
            response = self.client.get(url)
            response.raise_for_status()
            logger.info("Authentication test successful")
            return True
        except Exception as e:
            logger.error(f"Authentication test failed: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the API service.
        
        Returns:
            Dict containing health status information
        """
        url = urljoin(self.base_url, '/health')
        
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Utility function for creating a configured client
def create_client() -> WebJusticeClient:
    """
    Create a WebJusticeClient with default configuration.
    
    Returns:
        Configured WebJusticeClient instance
    """
    return WebJusticeClient()