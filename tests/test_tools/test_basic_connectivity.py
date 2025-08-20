"""
Basic connectivity test for Justice Agent tools.
Simple script to verify API connection and basic functionality.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Hardcoded API Key for testing
API_KEY = "ai_agent_Dbq48ZxiJXy712hEAEXd_LnsA-qws5cx"

# Add the tools directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))

from integrations.web_justice_client import WebJusticeClient, WebJusticeAPIError

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_basic_connectivity():
    """Test basic connectivity to the API."""
    print("🔌 Testing Basic API Connectivity")
    print("=" * 40)
    
    # Set hardcoded API key
    os.environ['WEB_JUSTICE_API_KEY'] = API_KEY
    
    api_key = API_KEY
    api_url = os.getenv('WEB_JUSTICE_API_URL', 'http://localhost:8000')
    
    print(f"🔑 API Key (hardcoded): {api_key[:12]}...{api_key[-4:]}")
    
    if not api_key:
        print("❌ WEB_JUSTICE_API_KEY not set")
        print("Set it with: export WEB_JUSTICE_API_KEY='your_key'")
        return False
    
    print(f"🌐 API URL: {api_url}")
    print(f"🔑 API Key: {'*' * (len(api_key) - 4)}{api_key[-4:]}")
    
    try:
        # Create client
        client = WebJusticeClient()
        print("✅ Client created successfully")
        
        # Test authentication
        print("🔐 Testing authentication...")
        if client.test_authentication():
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return False
        
        # Test health check
        print("🏥 Testing health check...")
        health = client.health_check()
        print(f"✅ Health status: {health.get('status', 'unknown')}")
        
        # Test search initiation (this should fail gracefully)
        print("🔍 Testing search initiation...")
        try:
            result = client.initiate_search("12345678909", "document")
            print(f"✅ Search initiated: {result.get('job_id', 'no job id')}")
            
            # Test status check if we got a job ID
            job_id = result.get('job_id')
            if job_id:
                print(f"📊 Testing status check for job: {job_id}")
                status = client.get_search_status(job_id)
                print(f"✅ Status retrieved: {status.get('current_status', 'unknown')}")
                
        except WebJusticeAPIError as e:
            print(f"⚠️ Search test failed (expected): {str(e)}")
        
        client.close()
        print("\n🎉 Basic connectivity test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Connectivity test failed: {str(e)}")
        return False


def test_tool_imports():
    """Test that tools can be imported."""
    print("\n🔧 Testing Tool Imports")
    print("=" * 40)
    
    try:
        from process_consultation import consult_process
        print("✅ Process consultation tool imported")
        
        from document_consultation import consult_document  
        print("✅ Document consultation tool imported")
        
        from utils.process_validator import validate_process_number
        print("✅ Process validator imported")
        
        from utils.document_validator import validate_cpf
        print("✅ Document validator imported")
        
        print("\n🎉 All tools imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Tool import failed: {str(e)}")
        return False


def main():
    """Main function."""
    print("🧪 Justice Agent Basic Connectivity Test")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test imports first
    if not test_tool_imports():
        print("\n❌ Tool import test failed")
        return 1
    
    # Test connectivity
    if not test_basic_connectivity():
        print("\n❌ Connectivity test failed")
        return 1
    
    print("\n✅ All basic tests passed!")
    print("\n💡 Next step: Run the full API simulation test")
    print("   python test_api_simulation.py")
    print("\n🐳 Don't forget to check your Docker containers:")
    print("   docker-compose ps")
    print("   docker-compose logs -f worker-ai-searches")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())