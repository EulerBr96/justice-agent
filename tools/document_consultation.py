"""
Document Consultation Tool for AI Agent.
Handles CPF/CNPJ queries by calling the Web Justice API and returning structured JSON data.
This tool is prepared for future use when document-based searches are enabled.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import asdict

# Add the tools directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrations.web_justice_client import WebJusticeClient, WebJusticeAPIError
from utils.polling_manager import poll_search_completion, PollingTimeoutError, create_progress_logger
from utils.document_validator import extract_first_document, DocumentValidationError, identify_document_type, get_clean_document

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocumentConsultationError(Exception):
    """Custom exception for document consultation errors."""
    pass


class DocumentConsultationTool:
    """
    AI Agent tool for consulting legal processes by CPF/CNPJ via Web Justice API.
    Note: This tool is prepared for future use when document-based searches are activated.
    """
    
    def __init__(self):
        """Initialize the document consultation tool."""
        self.client = None
        logger.info("DocumentConsultationTool initialized")
    
    def _get_client(self) -> WebJusticeClient:
        """Get or create API client."""
        if not self.client:
            try:
                self.client = WebJusticeClient()
                # Test authentication on first use
                if not self.client.test_authentication():
                    raise DocumentConsultationError("API authentication failed")
            except Exception as e:
                raise DocumentConsultationError(f"Failed to initialize API client: {str(e)}")
        return self.client
    
    def consult_document(self, user_input: str) -> Dict[str, Any]:
        """
        Main method to consult processes for a CPF/CNPJ based on user input.
        
        Args:
            user_input: User message containing CPF or CNPJ
            
        Returns:
            Dict containing process information or error details
        """
        try:
            logger.info(f"Processing document consultation request: {user_input[:100]}...")
            
            # Extract document from user input
            document = self._extract_document(user_input)
            if not document:
                return self._create_error_response(
                    "NO_DOCUMENT_FOUND",
                    "No valid CPF or CNPJ found in your message. Please provide a valid CPF (XXX.XXX.XXX-XX) or CNPJ (XX.XXX.XXX/XXXX-XX)."
                )
            
            # Identify document type
            doc_type = identify_document_type(document)
            logger.info(f"Extracted {doc_type}: {document}")
            
            # Get API client
            client = self._get_client()
            
            # Use clean document (numbers only) for API call
            clean_document = get_clean_document(document)
            
            # Initiate search
            search_response = self._initiate_search(client, clean_document)
            job_id = search_response.get('job_id')
            
            if not job_id:
                return self._create_error_response(
                    "SEARCH_INITIATION_FAILED", 
                    "Failed to initiate search - no job ID returned"
                )
            
            # Poll for completion
            final_status = self._poll_for_completion(client, job_id, clean_document)
            
            # Get results
            results = self._get_search_results(client, clean_document)
            
            # Return structured response
            return self._create_success_response(results, document, doc_type, search_response)
            
        except DocumentConsultationError as e:
            logger.error(f"Document consultation error: {str(e)}")
            return self._create_error_response("CONSULTATION_ERROR", str(e))
        except Exception as e:
            logger.error(f"Unexpected error during document consultation: {str(e)}")
            return self._create_error_response("UNEXPECTED_ERROR", f"An unexpected error occurred: {str(e)}")
    
    def _extract_document(self, user_input: str) -> Optional[str]:
        """Extract CPF/CNPJ from user input."""
        try:
            return extract_first_document(user_input)
        except DocumentValidationError as e:
            logger.warning(f"Document validation error: {str(e)}")
            return None
    
    def _initiate_search(self, client: WebJusticeClient, document: str) -> Dict[str, Any]:
        """Initiate search for the document."""
        try:
            return client.initiate_search(document, search_type="document")
        except WebJusticeAPIError as e:
            raise DocumentConsultationError(f"Failed to initiate search: {str(e)}")
    
    def _poll_for_completion(self, client: WebJusticeClient, job_id: str, document: str) -> Dict[str, Any]:
        """Poll for search completion."""
        try:
            progress_callback = create_progress_logger(f"Document {document} search")
            return poll_search_completion(client, job_id, progress_callback)
        except PollingTimeoutError as e:
            raise DocumentConsultationError(f"Search timed out: {str(e)}")
        except WebJusticeAPIError as e:
            raise DocumentConsultationError(f"Error during polling: {str(e)}")
    
    def _get_search_results(self, client: WebJusticeClient, document: str) -> Dict[str, Any]:
        """Get the final search results."""
        try:
            return client.get_processes(document)
        except WebJusticeAPIError as e:
            raise DocumentConsultationError(f"Failed to retrieve results: {str(e)}")
    
    def _create_success_response(self, results: Dict[str, Any], original_document: str, doc_type: str, search_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a successful response structure."""
        return {
            "status": "success",
            "tool": "document_consultation",
            "query": {
                "document": original_document,
                "document_type": doc_type,
                "search_type": "document"
            },
            "search_info": {
                "job_id": search_info.get('job_id'),
                "user_id": search_info.get('user_id'),
                "user_role": search_info.get('user_role')
            },
            "data": results,
            "summary": {
                "total_processes": results.get('total_processos', 0),
                "document_searched": results.get('documento', original_document),
                "search_completed_at": results.get('search_completed_at')
            }
        }
    
    def _create_error_response(self, error_code: str, error_message: str) -> Dict[str, Any]:
        """Create an error response structure."""
        return {
            "status": "error",
            "tool": "document_consultation",
            "error": {
                "code": error_code,
                "message": error_message
            },
            "data": None
        }
    
    def close(self):
        """Clean up resources."""
        if self.client:
            self.client.close()


# Main function for CLI usage
def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "error": {
                "code": "MISSING_INPUT",
                "message": "Please provide user input as command line argument"
            }
        }))
        sys.exit(1)
    
    user_input = " ".join(sys.argv[1:])
    
    tool = DocumentConsultationTool()
    try:
        result = tool.consult_document(user_input)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        tool.close()


# Function for programmatic usage
def consult_document(user_input: str) -> Dict[str, Any]:
    """
    Programmatic interface for document consultation.
    
    Args:
        user_input: User message containing CPF or CNPJ
        
    Returns:
        Dict containing process information or error details
    """
    tool = DocumentConsultationTool()
    try:
        return tool.consult_document(user_input)
    finally:
        tool.close()


if __name__ == "__main__":
    main()