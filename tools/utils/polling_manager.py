"""
Polling manager for Web Justice API operations.
Handles smart polling with exponential backoff for search status monitoring.
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PollingConfig:
    """Configuration for polling behavior."""
    initial_interval: float = 2.0      # Start with 2 seconds
    max_interval: float = 30.0         # Maximum 30 seconds between polls
    backoff_multiplier: float = 1.5    # Exponential backoff factor
    max_wait_time: float = 900.0       # Maximum total wait time (15 minutes)
    timeout_buffer: float = 30.0       # Buffer before timeout to allow graceful completion


class PollingTimeoutError(Exception):
    """Raised when polling times out."""
    pass


class PollingManager:
    """
    Manages intelligent polling with exponential backoff for API operations.
    """
    
    def __init__(self, config: Optional[PollingConfig] = None):
        """
        Initialize the polling manager.
        
        Args:
            config: Polling configuration (uses defaults if not provided)
        """
        self.config = config or PollingConfig()
        self.reset()
    
    def reset(self):
        """Reset polling state for a new operation."""
        self.start_time = time.time()
        self.current_interval = self.config.initial_interval
        self.poll_count = 0
    
    def should_continue_polling(self) -> bool:
        """
        Check if polling should continue based on elapsed time.
        
        Returns:
            True if polling should continue, False if timeout reached
        """
        elapsed = time.time() - self.start_time
        return elapsed < (self.config.max_wait_time - self.config.timeout_buffer)
    
    def wait_for_next_poll(self):
        """
        Wait for the appropriate interval before next poll and update interval.
        """
        logger.debug(f"Waiting {self.current_interval:.1f}s before next poll (attempt {self.poll_count + 1})")
        time.sleep(self.current_interval)
        
        # Update interval for next poll with exponential backoff
        self.current_interval = min(
            self.current_interval * self.config.backoff_multiplier,
            self.config.max_interval
        )
        self.poll_count += 1
    
    def get_polling_stats(self) -> Dict[str, Any]:
        """
        Get current polling statistics.
        
        Returns:
            Dict with polling statistics
        """
        elapsed = time.time() - self.start_time
        return {
            "elapsed_time": elapsed,
            "poll_count": self.poll_count,
            "current_interval": self.current_interval,
            "time_remaining": max(0, self.config.max_wait_time - elapsed)
        }
    
    def poll_until_complete(
        self, 
        status_checker: Callable[[], Dict[str, Any]], 
        completion_checker: Callable[[Dict[str, Any]], bool],
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Poll for completion using provided checker functions.
        
        Args:
            status_checker: Function that returns current status
            completion_checker: Function that checks if status indicates completion
            progress_callback: Optional callback for progress updates
            
        Returns:
            Final status when completion is detected
            
        Raises:
            PollingTimeoutError: If maximum wait time is exceeded
        """
        self.reset()
        logger.info(f"Starting polling with max wait time: {self.config.max_wait_time}s")
        
        while self.should_continue_polling():
            try:
                # Get current status
                status = status_checker()
                
                # Log current status
                current_status = status.get('current_status', 'Unknown')
                progress = status.get('progress_percentage', 0)
                phase = status.get('current_phase', 'Unknown')
                
                logger.info(f"Poll #{self.poll_count + 1}: {current_status} - {progress}% ({phase})")
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(status)
                
                # Check if complete
                if completion_checker(status):
                    stats = self.get_polling_stats()
                    logger.info(f"Polling completed after {stats['elapsed_time']:.1f}s and {stats['poll_count']} attempts")
                    return status
                
                # Wait before next poll
                self.wait_for_next_poll()
                
            except Exception as e:
                logger.error(f"Error during polling attempt {self.poll_count + 1}: {str(e)}")
                # Still wait before retrying to avoid hammering the API
                self.wait_for_next_poll()
        
        # Timeout reached
        stats = self.get_polling_stats()
        error_msg = f"Polling timeout after {stats['elapsed_time']:.1f}s and {stats['poll_count']} attempts"
        logger.error(error_msg)
        raise PollingTimeoutError(error_msg)


def poll_search_completion(client, job_id: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Convenience function to poll for search completion.
    
    Args:
        client: WebJusticeClient instance
        job_id: Search job identifier
        progress_callback: Optional callback for progress updates
        
    Returns:
        Final search status when complete
        
    Raises:
        PollingTimeoutError: If polling times out
    """
    polling_manager = PollingManager()
    
    def status_checker():
        return client.get_search_status(job_id)
    
    def completion_checker(status):
        return status.get('is_ready_for_consultation', False)
    
    return polling_manager.poll_until_complete(
        status_checker=status_checker,
        completion_checker=completion_checker,
        progress_callback=progress_callback
    )


def create_progress_logger(job_description: str = "Search") -> Callable:
    """
    Create a progress callback that logs updates.
    
    Args:
        job_description: Description of the job being polled
        
    Returns:
        Progress callback function
    """
    def progress_callback(status: Dict[str, Any]):
        current_status = status.get('current_status', 'Unknown')
        progress = status.get('progress_percentage', 0)
        phase = status.get('current_phase', 'Unknown')
        
        logger.info(f"{job_description} progress: {current_status} - {progress}% ({phase})")
    
    return progress_callback