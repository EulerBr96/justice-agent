"""
Teste rápido de consulta por número de processo.
"""

import os
import sys
import time

# Hardcoded API Key for testing
API_KEY = "ai_agent_Dbq48ZxiJXy712hEAEXd_LnsA-qws5cx"

# Add the tools directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))

from process_consultation import consult_process

def test_process_consultation():
    """Teste com número de processo real."""
    print("⚖️ Process Consultation Test - 6140319-91.2024.8.09.0051")
    print("=" * 50)
    
    try:
        start = time.time()
        result = consult_process("Consultar processo 6140319-91.2024.8.09.0051")
        end = time.time()
        
        print(f"⏱️ Completed in {end - start:.1f}s")
        print(f"📊 Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            summary = result.get('summary', {})
            print(f"✅ Found {summary.get('total_processes', 0)} processes")
        else:
            error = result.get('error', {})
            print(f"❌ Error: {error.get('message', 'Unknown')}")
        
        return result.get('status') == 'success'
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    # Set the hardcoded API key in environment
    os.environ['WEB_JUSTICE_API_KEY'] = API_KEY
    print(f"🔧 Using hardcoded API Key: {API_KEY[:12]}...{API_KEY[-4:]}")
    
    success = test_process_consultation()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)