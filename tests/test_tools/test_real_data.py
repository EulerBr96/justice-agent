"""
Test script with real data to demonstrate the complete AI Agent workflow.
Uses real process numbers to show the system working with actual data.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

# Hardcoded API Key for testing
API_KEY = "ai_agent_ZxlYxQqmNMEvMYrS20yDyb7Nlol6Go3e"

# Add the tools directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))

# Import our tools
from process_consultation import consult_process

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'test_real_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


def test_real_process_consultation():
    """Test process consultation with real process number.""" 
    print("\n⚖️ Testing Real Process Consultation")
    print("=" * 50)
    
    # Real process: 6140319-91.2024.8.09.0051
    test_input = "Preciso de informações sobre o processo 6140319-91.2024.8.09.0051"
    
    print(f"📝 Input: {test_input}")
    print("📞 Making API call...")
    
    try:
        start_time = time.time()
        result = consult_process(test_input)
        end_time = time.time()
        
        print(f"⏱️ Completed in {end_time - start_time:.2f} seconds")
        print(f"📊 Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            summary = result.get('summary', {})
            print(f"✅ Found {summary.get('total_processes', 0)} processes")
            print(f"📅 Search completed at: {summary.get('search_completed_at')}")
        
        print("\n📄 Full Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {'status': 'error', 'error': str(e)}


def monitor_docker_logs():
    """Show commands to monitor Docker logs."""
    print("\n🐳 Monitor Docker Logs")
    print("=" * 50)
    print("Execute these commands in separate terminals:")
    print()
    print("# AI Workers:")
    print("docker-compose logs -f worker-ai-searches")
    print("docker-compose logs -f worker-ai-details") 
    print("docker-compose logs -f worker-ai-document-extractor")
    print()
    print("# API Gateway:")
    print("docker-compose logs -f api-gateway-v2")
    print()
    print("# All services:")
    print("docker-compose logs -f")


def main():
    """Main test function."""
    print("🤖 Justice Agent Real Data Test")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📊 Test Data:")
    print("  • Process: 6140319-91.2024.8.09.0051")
    
    # Set hardcoded API key
    os.environ['WEB_JUSTICE_API_KEY'] = API_KEY
    
    print(f"\n✅ API Key configured (hardcoded): {API_KEY[:12]}...{API_KEY[-4:]}")
    
    # Show monitoring info
    monitor_docker_logs()
    
    print(f"\n{'='*50}")
    print("🚀 Starting Process Consultation Test")
    print(f"{'='*50}")
    
    # Test: Process consultation with real process number
    proc_result = test_real_process_consultation()
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    proc_status = "✅ SUCCESS" if proc_result.get('status') == 'success' else "❌ FAILED"
    
    print(f"Process Consultation: {proc_status}")
    
    if proc_result.get('status') == 'success':
        proc_summary = proc_result.get('summary', {})
        print(f"• Process found {proc_summary.get('total_processes', 0)} results")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Detailed logs saved to file")
    
    return 0


if __name__ == "__main__":
    print(f"🔧 Using hardcoded API Key: {API_KEY[:12]}...{API_KEY[-4:]}")
    sys.exit(main())