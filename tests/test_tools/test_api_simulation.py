"""
Test script to simulate AI Agent API calls for monitoring Docker containers.
This script demonstrates the complete workflow of both tools making real API calls
to the web-justice-v0 system running locally.
"""

import os
import sys
import json
import time
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime

# Add the tools directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))

# Import our tools
from process_consultation import consult_process
from document_consultation import consult_document

# Configure logging to see detailed API interaction
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'test_api_simulation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


class APISimulationTest:
    """
    Simulates AI Agent API calls to test the complete workflow.
    """
    
    def __init__(self):
        """Initialize the test suite."""
        self.test_results = []
        
    def log_test_result(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test result for summary."""
        result = {
            'test_name': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        logger.info(f"{status_emoji} {test_name}: {status}")
        
    def check_environment(self) -> bool:
        """Check if environment is properly configured."""
        logger.info("🔍 Checking environment configuration...")
        
        api_key = os.getenv('WEB_JUSTICE_API_KEY')
        api_url = os.getenv('WEB_JUSTICE_API_URL', 'http://localhost:8000')
        
        if not api_key:
            logger.error("❌ WEB_JUSTICE_API_KEY not set")
            logger.info("Set the environment variable:")
            logger.info("export WEB_JUSTICE_API_KEY='your_api_key_here'")
            return False
            
        logger.info(f"✅ API URL: {api_url}")
        logger.info(f"✅ API Key: {'*' * (len(api_key) - 4)}{api_key[-4:]}")
        return True
        
    def test_process_consultation(self) -> Dict[str, Any]:
        """Test process consultation tool with a valid process number."""
        test_name = "Process Consultation"
        logger.info(f"\n🚀 Starting {test_name} Test")
        
        # Use a test process number (this will likely not exist but will test the workflow)
        test_input = "I need information about process 1234567-89.2023.1.01.0001"
        
        try:
            logger.info("📞 Making API call to process consultation tool...")
            result = consult_process(test_input)
            
            self.log_test_result(test_name, result.get('status', 'unknown'), result)
            
            # Log detailed result
            logger.info("📄 Response received:")
            logger.info(json.dumps(result, indent=2, ensure_ascii=False))
            
            return result
            
        except Exception as e:
            error_details = {'error': str(e), 'input': test_input}
            self.log_test_result(test_name, "error", error_details)
            logger.error(f"❌ Process consultation failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def test_document_consultation(self) -> Dict[str, Any]:
        """Test document consultation tool with a valid CPF."""
        test_name = "Document Consultation"
        logger.info(f"\n🚀 Starting {test_name} Test")
        
        # Use a test CPF (this will likely not exist but will test the workflow)
        test_input = "I need to search for processes related to CPF 123.456.789-09"
        
        try:
            logger.info("📞 Making API call to document consultation tool...")
            result = consult_document(test_input)
            
            self.log_test_result(test_name, result.get('status', 'unknown'), result)
            
            # Log detailed result
            logger.info("📄 Response received:")
            logger.info(json.dumps(result, indent=2, ensure_ascii=False))
            
            return result
            
        except Exception as e:
            error_details = {'error': str(e), 'input': test_input}
            self.log_test_result(test_name, "error", error_details)
            logger.error(f"❌ Document consultation failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def test_cnpj_consultation(self) -> Dict[str, Any]:
        """Test document consultation tool with a CNPJ."""
        test_name = "CNPJ Consultation"
        logger.info(f"\n🚀 Starting {test_name} Test")
        
        # Use a test CNPJ
        test_input = "Please search for legal processes involving CNPJ 11.222.333/0001-81"
        
        try:
            logger.info("📞 Making API call to document consultation tool...")
            result = consult_document(test_input)
            
            self.log_test_result(test_name, result.get('status', 'unknown'), result)
            
            # Log detailed result
            logger.info("📄 Response received:")
            logger.info(json.dumps(result, indent=2, ensure_ascii=False))
            
            return result
            
        except Exception as e:
            error_details = {'error': str(e), 'input': test_input}
            self.log_test_result(test_name, "error", error_details)
            logger.error(f"❌ CNPJ consultation failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def test_multiple_processes(self) -> Dict[str, Any]:
        """Test with multiple process numbers in sequence."""
        test_name = "Multiple Processes"
        logger.info(f"\n🚀 Starting {test_name} Test")
        
        process_numbers = [
            "7654321-12.2024.8.26.1234",
            "9876543-21.2023.4.02.5678",
            "1111111-22.2022.1.01.9999"
        ]
        
        results = []
        
        for i, process_num in enumerate(process_numbers, 1):
            logger.info(f"🔄 Testing process {i}/{len(process_numbers)}: {process_num}")
            test_input = f"Get details for process {process_num}"
            
            try:
                result = consult_process(test_input)
                results.append({
                    'process': process_num,
                    'result': result
                })
                
                # Brief delay between requests
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Failed for process {process_num}: {str(e)}")
                results.append({
                    'process': process_num,
                    'result': {'status': 'error', 'error': str(e)}
                })
        
        summary = {
            'total_tests': len(process_numbers),
            'successful': len([r for r in results if r['result'].get('status') == 'success']),
            'failed': len([r for r in results if r['result'].get('status') == 'error']),
            'results': results
        }
        
        self.log_test_result(test_name, "completed", summary)
        
        return summary
    
    def print_test_summary(self):
        """Print a summary of all tests performed."""
        logger.info("\n" + "="*60)
        logger.info("📊 TEST SUMMARY")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        successful = len([r for r in self.test_results if r['status'] == 'success'])
        errors = len([r for r in self.test_results if r['status'] == 'error'])
        warnings = len([r for r in self.test_results if r['status'] == 'warning'])
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Successful: {successful}")
        logger.info(f"❌ Errors: {errors}")
        logger.info(f"⚠️ Warnings: {warnings}")
        
        logger.info("\nDetailed Results:")
        for result in self.test_results:
            status_emoji = "✅" if result['status'] == "success" else "❌" if result['status'] == "error" else "⚠️"
            logger.info(f"{status_emoji} {result['test_name']}: {result['status']} at {result['timestamp']}")
        
        logger.info("\n📝 Log files created for detailed analysis")
        logger.info("🐳 Check Docker containers for worker logs:")
        logger.info("  docker-compose logs -f worker-ai-searches")
        logger.info("  docker-compose logs -f worker-ai-details")  
        logger.info("  docker-compose logs -f worker-ai-documents")


def main():
    """Main test execution function."""
    print("🤖 AI Agent API Simulation Test Suite")
    print("=" * 50)
    
    test_suite = APISimulationTest()
    
    # Check environment first
    if not test_suite.check_environment():
        print("\n❌ Environment check failed. Please configure API key.")
        sys.exit(1)
    
    print("\n🎯 This test will:")
    print("1. Make real API calls to your local web-justice-v0 system")
    print("2. Trigger the AI workers you've just implemented")
    print("3. Generate logs for you to monitor in Docker containers")
    print("4. Test both process and document consultation workflows")
    
    input("\n⏸️ Press Enter to continue (make sure your Docker containers are running)...")
    
    # Run all tests
    logger.info("🚀 Starting API simulation tests...")
    
    # Test individual tools
    test_suite.test_process_consultation()
    time.sleep(3)  # Brief pause between tests
    
    test_suite.test_document_consultation()
    time.sleep(3)
    
    test_suite.test_cnpj_consultation()
    time.sleep(3)
    
    # Test multiple processes
    test_suite.test_multiple_processes()
    
    # Print summary
    test_suite.print_test_summary()
    
    print("\n🏁 Test suite completed!")
    print("\n💡 Next steps:")
    print("1. Check the Docker container logs to see worker activity")
    print("2. Review the generated log file for detailed API interactions")
    print("3. Verify that the AI workers are processing tasks correctly")
    print("\n🐳 Useful Docker commands:")
    print("  docker-compose logs -f --tail=50 worker-ai-searches")
    print("  docker-compose logs -f --tail=50 worker-ai-details")
    print("  docker-compose logs -f --tail=50 worker-ai-documents")
    print("  docker-compose ps  # Check all services status")


if __name__ == "__main__":
    main()