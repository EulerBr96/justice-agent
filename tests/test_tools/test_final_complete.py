"""
Teste final completo do sistema AI Agent.
Testa ambos os workflows com dados reais e verifica toda a integração.
"""

import os
import sys
import json
import time
from datetime import datetime

# Hardcoded API Key for testing
API_KEY = "ai_agent_Dbq48ZxiJXy712hEAEXd_LnsA-qws5cx"

# Add the tools directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))

from document_consultation import consult_document
from process_consultation import consult_process

def test_complete_workflow():
    """Teste completo do workflow AI Agent."""
    print("🚀 TESTE FINAL COMPLETO - AI AGENT SYSTEM")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set the hardcoded API key in environment
    os.environ['WEB_JUSTICE_API_KEY'] = API_KEY
    
    api_key = API_KEY
    print(f"🔑 API Key (hardcoded): {api_key[:12]}...{api_key[-4:]}")
    print()
    
    results = []
    
    # Teste 1: Consulta por CPF
    print("📋 TESTE 1: Consulta por CPF")
    print("-" * 40)
    try:
        start = time.time()
        result1 = consult_document("CPF 442.327.038-29")
        end = time.time()
        
        success1 = result1.get('status') == 'success'
        results.append(success1)
        
        print(f"⏱️ Tempo: {end - start:.1f}s")
        print(f"📊 Status: {result1.get('status')}")
        if success1:
            summary = result1.get('summary', {})
            print(f"✅ Processos encontrados: {summary.get('total_processes', 0)}")
        else:
            error = result1.get('error', {})
            print(f"❌ Erro: {error.get('message', 'Unknown')}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        results.append(False)
    
    print()
    
    # Teste 2: Consulta por Processo
    print("📋 TESTE 2: Consulta por Número de Processo")
    print("-" * 40)
    try:
        start = time.time()
        result2 = consult_process("Processo 6140319-91.2024.8.09.0051")
        end = time.time()
        
        success2 = result2.get('status') == 'success'
        results.append(success2)
        
        print(f"⏱️ Tempo: {end - start:.1f}s")
        print(f"📊 Status: {result2.get('status')}")
        if success2:
            summary = result2.get('summary', {})
            print(f"✅ Processos encontrados: {summary.get('total_processes', 0)}")
        else:
            error = result2.get('error', {})
            print(f"❌ Erro: {error.get('message', 'Unknown')}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        results.append(False)
    
    print()
    
    # Teste 3: Consulta por CNPJ
    print("📋 TESTE 3: Consulta por CNPJ")
    print("-" * 40)
    try:
        start = time.time()
        result3 = consult_document("CNPJ 11.222.333/0001-81")
        end = time.time()
        
        success3 = result3.get('status') == 'success'
        results.append(success3)
        
        print(f"⏱️ Tempo: {end - start:.1f}s")
        print(f"📊 Status: {result3.get('status')}")
        if success3:
            summary = result3.get('summary', {})
            print(f"✅ Processos encontrados: {summary.get('total_processes', 0)}")
        else:
            error = result3.get('error', {})
            print(f"❌ Erro: {error.get('message', 'Unknown')}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        results.append(False)
    
    # Resumo final
    total_tests = len(results)
    successful_tests = sum(results)
    
    print()
    print("=" * 60)
    print("📊 RESUMO FINAL")
    print("=" * 60)
    print(f"Total de testes: {total_tests}")
    print(f"✅ Sucessos: {successful_tests}")
    print(f"❌ Falhas: {total_tests - successful_tests}")
    print(f"📈 Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print()
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 Sistema AI Agent 100% funcional!")
        print()
        print("✅ Componentes funcionais:")
        print("  • API Gateway v2")
        print("  • Worker AI Searches")
        print("  • Worker AI Details")
        print("  • Database Integration")
        print("  • Justice Agent Tools")
        print("  • Polling System")
        print("  • JSON Response Format")
        print()
        print("🏗️ Arquitetura validada:")
        print("  AI Agent → API → Queue → Worker → Database → Response")
        
        return True
    else:
        print()
        print("⚠️ Alguns testes falharam")
        return False

if __name__ == "__main__":
    print(f"🔧 Using hardcoded API Key: {API_KEY[:12]}...{API_KEY[-4:]}")
    success = test_complete_workflow()
    sys.exit(0 if success else 1)