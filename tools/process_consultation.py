"""
Process Consultation Tool for AI Agent.
Handles process number queries by calling the Web Justice API and returning structured JSON data.
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
from utils.process_validator import extract_first_process, ProcessValidationError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProcessConsultationError(Exception):
    """Custom exception for process consultation errors."""
    pass


class ProcessConsultationTool:
    """
    AI Agent tool for consulting legal process information via Web Justice API.
    """
    
    def __init__(self):
        """Initialize the process consultation tool."""
        self.client = None
        logger.info("ProcessConsultationTool initialized")
    
    def _get_client(self) -> WebJusticeClient:
        """Get or create API client."""
        if not self.client:
            try:
                self.client = WebJusticeClient()
                # Test authentication on first use
                if not self.client.test_authentication():
                    raise ProcessConsultationError("API authentication failed")
            except Exception as e:
                raise ProcessConsultationError(f"Failed to initialize API client: {str(e)}")
        return self.client
    
    def consult_process(self, user_input: str) -> Dict[str, Any]:
        """
        Main method to consult a process based on user input.
        
        Args:
            user_input: User message containing process number
            
        Returns:
            Dict containing process information or error details
        """
        try:
            logger.info(f"Processing consultation request: {user_input[:100]}...")
            
            # Extract process number from user input
            process_number = self._extract_process_number(user_input)
            if not process_number:
                return self._create_error_response(
                    "NO_PROCESS_FOUND",
                    "No valid process number found in your message. Please provide a process number in the format: NNNNNNN-DD.AAAA.J.TR.OOOO"
                )
            
            logger.info(f"Extracted process number: {process_number}")
            
            # Get API client
            client = self._get_client()
            
            # Initiate search
            search_response = self._initiate_search(client, process_number)
            job_id = search_response.get('job_id')
            
            if not job_id:
                return self._create_error_response(
                    "SEARCH_INITIATION_FAILED", 
                    "Failed to initiate search - no job ID returned"
                )
            
            # Poll for completion
            final_status = self._poll_for_completion(client, job_id, process_number)
            
            # Get results
            results = self._get_search_results(client, process_number)
            
            # Return structured response
            return self._create_success_response(results, process_number, search_response)
            
        except ProcessConsultationError as e:
            logger.error(f"Process consultation error: {str(e)}")
            return self._create_error_response("CONSULTATION_ERROR", str(e))
        except Exception as e:
            logger.error(f"Unexpected error during process consultation: {str(e)}")
            return self._create_error_response("UNEXPECTED_ERROR", f"An unexpected error occurred: {str(e)}")
    
    def _extract_process_number(self, user_input: str) -> Optional[str]:
        """Extract process number from user input."""
        try:
            return extract_first_process(user_input)
        except ProcessValidationError as e:
            logger.warning(f"Process validation error: {str(e)}")
            return None
    
    def _initiate_search(self, client: WebJusticeClient, process_number: str) -> Dict[str, Any]:
        """Initiate search for the process number."""
        try:
            return client.initiate_search(process_number, search_type="process")
        except WebJusticeAPIError as e:
            raise ProcessConsultationError(f"Failed to initiate search: {str(e)}")
    
    def _poll_for_completion(self, client: WebJusticeClient, job_id: str, process_number: str) -> Dict[str, Any]:
        """Poll for search completion."""
        try:
            progress_callback = create_progress_logger(f"Process {process_number} search")
            return poll_search_completion(client, job_id, progress_callback)
        except PollingTimeoutError as e:
            raise ProcessConsultationError(f"Search timed out: {str(e)}")
        except WebJusticeAPIError as e:
            raise ProcessConsultationError(f"Error during polling: {str(e)}")
    
    def _get_search_results(self, client: WebJusticeClient, process_number: str) -> Dict[str, Any]:
        """Get the final search results."""
        try:
            return client.get_processes(process_number)
        except WebJusticeAPIError as e:
            raise ProcessConsultationError(f"Failed to retrieve results: {str(e)}")
    
    def _create_success_response(self, results: Dict[str, Any], process_number: str, search_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a successful response structure."""
        # Compat layer: API pode retornar data_details (novo) ou data (antigo)
        details = results.get('data_details') or results.get('data') or results
        return {
            "status": "success",
            "tool": "process_consultation",
            "query": {
                "process_number": process_number,
                "search_type": "process"
            },
            "search_info": {
                "job_id": search_info.get('job_id'),
                "user_id": search_info.get('user_id'),
                "user_role": search_info.get('user_role')
            },
            "data_details": results,
            "summary": {
                "total_processes": details.get('total_processos', 0),
                "document_searched": details.get('documento', process_number),
                "search_completed_at": details.get('search_completed_at')
            }
        }
    
    def _create_error_response(self, error_code: str, error_message: str) -> Dict[str, Any]:
        """Create an error response structure."""
        return {
            "status": "error",
            "tool": "process_consultation",
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
    
    tool = ProcessConsultationTool()
    try:
        result = tool.consult_process(user_input)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        tool.close()


# Function for programmatic usage
def consult_process(user_input: str) -> Dict[str, Any]:
    """
    Programmatic interface for process consultation.
    
    Args:
        user_input: User message containing process number
        
    Returns:
        Dict containing process information or error details
    """
    tool = ProcessConsultationTool()
    try:
        return tool.consult_process(user_input)
    finally:
        tool.close()


if __name__ == "__main__":
    main()