"""
Test script for Justice Agent tools.
Basic functionality and integration testing.
"""

import os
import sys
import json
import logging
from typing import Dict, Any

# Add the tools directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_process_validator():
    """Test process number validation functionality."""
    print("\n=== Testing Process Validator ===")
    
    from utils.process_validator import extract_process_numbers, validate_process_number, normalize_process_number
    
    # Test cases
    test_cases = [
        "Process number: 1234567-89.2023.1.01.0001",
        "I need info about processo 7654321-12.2024.8.26.1234",
        "Can you help with 1111111222023101000110?",  # 20 digits
        "No process number here",
        "Multiple: 1234567-89.2023.1.01.0001 and 7654321-12.2024.8.26.1234"
    ]
    
    for case in test_cases:
        extracted = extract_process_numbers(case)
        print(f"Input: {case}")
        print(f"Extracted: {extracted}")
        for proc in extracted:
            print(f"  Valid: {validate_process_number(proc)}")
        print()


def test_document_validator():
    """Test document validation functionality."""
    print("\n=== Testing Document Validator ===")
    
    from utils.document_validator import extract_documents, validate_cpf, validate_cnpj, identify_document_type
    
    # Test cases
    test_cases = [
        "CPF: 123.456.789-09",
        "My CNPJ is 11.222.333/0001-81",
        "Document: 12345678909",  # CPF without formatting
        "Company: 11222333000181",  # CNPJ without formatting  
        "Invalid: 123.456.789-00",  # Invalid CPF
        "No documents here"
    ]
    
    for case in test_cases:
        extracted = extract_documents(case)
        print(f"Input: {case}")
        print(f"Extracted: {extracted}")
        for doc in extracted:
            doc_type = identify_document_type(doc)
            print(f"  Type: {doc_type}")
            if doc_type == 'CPF':
                print(f"  Valid CPF: {validate_cpf(doc)}")
            elif doc_type == 'CNPJ':
                print(f"  Valid CNPJ: {validate_cnpj(doc)}")
        print()


def test_api_client():
    """Test API client functionality."""
    print("\n=== Testing API Client ===")
    
    try:
        from integrations.web_justice_client import WebJusticeClient
        
        # Check if API key is set
        api_key = os.getenv('WEB_JUSTICE_API_KEY')
        if not api_key:
            print("❌ WEB_JUSTICE_API_KEY not set - skipping API tests")
            print("To test API functionality, set the environment variable:")
            print("export WEB_JUSTICE_API_KEY='your_api_key_here'")
            return
        
        client = WebJusticeClient()
        
        # Test authentication
        print("Testing authentication...")
        auth_result = client.test_authentication()
        if auth_result:
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return
        
        # Test health check
        print("Testing health check...")
        health = client.health_check()
        print(f"Health status: {health.get('status', 'unknown')}")
        
        client.close()
        print("✅ API client tests completed")
        
    except Exception as e:
        print(f"❌ API client test failed: {str(e)}")


def test_process_consultation():
    """Test process consultation tool."""
    print("\n=== Testing Process Consultation Tool ===")
    
    # Check if API key is set
    api_key = os.getenv('WEB_JUSTICE_API_KEY')
    if not api_key:
        print("❌ WEB_JUSTICE_API_KEY not set - skipping consultation tests")
        return
    
    try:
        from process_consultation import consult_process
        
        # Test with a mock process number
        test_input = "I need information about process 1234567-89.2023.1.01.0001"
        print(f"Testing with: {test_input}")
        
        result = consult_process(test_input)
        print(f"Status: {result.get('status')}")
        
        if result.get('status') == 'error':
            print(f"Error: {result.get('error', {}).get('message', 'Unknown error')}")
        else:
            print(f"Query: {result.get('query', {})}")
            print(f"Summary: {result.get('summary', {})}")
        
        print("✅ Process consultation test completed")
        
    except Exception as e:
        print(f"❌ Process consultation test failed: {str(e)}")


def test_configuration():
    """Test configuration management."""
    print("\n=== Testing Configuration ===")
    
    try:
        from config import get_config, validate_config, ENV_VARS_HELP
        
        # Try to load configuration
        try:
            config = get_config()
            print("✅ Configuration loaded successfully")
            print(f"API URL: {config.api.base_url}")
            print(f"Has API Key: {'Yes' if config.api.api_key else 'No'}")
            
            # Validate configuration
            validation = validate_config(config)
            if validation['valid']:
                print("✅ Configuration is valid")
            else:
                print("❌ Configuration issues:")
                for error in validation['errors']:
                    print(f"  - {error}")
                    
            if validation['warnings']:
                print("⚠️ Configuration warnings:")
                for warning in validation['warnings']:
                    print(f"  - {warning}")
                    
        except Exception as e:
            print(f"❌ Configuration failed: {str(e)}")
            print("\nEnvironment Variables Help:")
            print(ENV_VARS_HELP)
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")


def main():
    """Run all tests."""
    print("Justice Agent Tools - Test Suite")
    print("=" * 40)
    
    # Basic functionality tests (no API required)
    test_process_validator()
    test_document_validator()
    test_configuration()
    
    # API-dependent tests (require API key)
    test_api_client()
    test_process_consultation()
    
    print("\n" + "=" * 40)
    print("Test suite completed!")
    print("\nTo run full integration tests:")
    print("1. Set WEB_JUSTICE_API_KEY environment variable")
    print("2. Ensure the Web Justice API is running and accessible")
    print("3. Run: python test_tools.py")


if __name__ == "__main__":
    main()