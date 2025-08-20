"""
Teste rápido para verificar se o workflow está funcionando com dados reais.
"""

import os
import sys
import json
import time

# Add the tools directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))

from document_consultation import consult_document

def quick_cpf_test():
    """Teste rápido com CPF real."""
    print("🧑 Quick CPF Test - 442.327.038-29")
    print("=" * 40)
    
    try:
        start = time.time()
        result = consult_document("CPF 442.327.038-29")
        end = time.time()
        
        print(f"⏱️ Completed in {end - start:.1f}s")
        print(f"📊 Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            summary = result.get('summary', {})
            print(f"✅ Found {summary.get('total_processes', 0)} processes")
            print(f"📄 Response size: {len(json.dumps(result))} chars")
        else:
            error = result.get('error', {})
            print(f"❌ Error: {error.get('message', 'Unknown')}")
        
        return result.get('status') == 'success'
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    api_key = os.getenv('WEB_JUSTICE_API_KEY')
    if not api_key:
        print("❌ WEB_JUSTICE_API_KEY not set")
        sys.exit(1)
    
    print("🚀 Quick Test Started")
    success = quick_cpf_test()
    
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)