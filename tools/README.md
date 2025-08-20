# Justice Agent Tools

AI Agent tools for consulting legal processes via the Web Justice API. This package provides two microservices for process consultation and document-based searches.

## Features

- **Process Consultation Tool**: Search by specific process numbers (CNJ format)
- **Document Consultation Tool**: Search by CPF/CNPJ (prepared for future use)
- **Smart Polling**: Exponential backoff with progress monitoring
- **Robust Validation**: CNJ format validation for process numbers and CPF/CNPJ validation
- **Error Handling**: Comprehensive error handling and logging
- **JSON Output**: Structured responses for AI Agent consumption

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set required environment variables:
```bash
export WEB_JUSTICE_API_KEY="your_api_key_here"
export WEB_JUSTICE_API_URL="http://your-api-url:8000"  # Optional, defaults to localhost
```

## Usage

### Process Consultation (Ready for Use)

```bash
# Command line usage
python process_consultation.py "I need information about process 1234567-89.2023.1.01.0001"

# Programmatic usage
from process_consultation import consult_process
result = consult_process("Process number: 1234567-89.2023.1.01.0001")
```

### Document Consultation (Future Use)

```bash
# Command line usage  
python document_consultation.py "Search for CPF 123.456.789-00"

# Programmatic usage
from document_consultation import consult_document
result = consult_document("CPF: 123.456.789-00")
```

## Response Format

### Success Response
```json
{
  "status": "success",
  "tool": "process_consultation",
  "query": {
    "process_number": "1234567-89.2023.1.01.0001",
    "search_type": "process"
  },
  "search_info": {
    "job_id": "abc123",
    "user_id": "ai_agent_456", 
    "user_role": "AI_AGENT"
  },
  "data": {
    "total_processos": 1,
    "documento": "1234567-89.2023.1.01.0001",
    "processos": [...]
  },
  "summary": {
    "total_processes": 1,
    "document_searched": "1234567-89.2023.1.01.0001",
    "search_completed_at": "2024-01-15T10:30:00Z"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "tool": "process_consultation", 
  "error": {
    "code": "NO_PROCESS_FOUND",
    "message": "No valid process number found in your message."
  },
  "data": null
}
```

## Architecture

### Core Components

- **WebJusticeClient**: HTTP client for API communication with authentication and error handling
- **PollingManager**: Smart polling with exponential backoff (2s → 30s, max 15 minutes)
- **ProcessValidator**: CNJ format validation and extraction
- **DocumentValidator**: CPF/CNPJ validation and extraction

### File Structure

```
justice_agent/tools/
├── process_consultation.py          # Main process consultation tool
├── document_consultation.py         # Main document consultation tool  
├── config.py                       # Configuration management
├── requirements.txt                # Dependencies
├── README.md                       # Documentation
├── integrations/
│   ├── __init__.py
│   └── web_justice_client.py        # API client
└── utils/
    ├── __init__.py
    ├── process_validator.py         # Process number validation
    ├── document_validator.py        # CPF/CNPJ validation
    └── polling_manager.py           # Polling logic
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `WEB_JUSTICE_API_KEY` | API authentication key | - | Yes |
| `WEB_JUSTICE_API_URL` | API base URL | `http://localhost:8000` | No |
| `WEB_JUSTICE_API_TIMEOUT` | Request timeout (seconds) | `30.0` | No |
| `POLLING_INITIAL_INTERVAL` | Initial polling interval (seconds) | `2.0` | No |
| `POLLING_MAX_INTERVAL` | Maximum polling interval (seconds) | `30.0` | No |
| `POLLING_MAX_WAIT_TIME` | Maximum total wait time (seconds) | `900.0` | No |
| `JUSTICE_TOOLS_LOG_LEVEL` | Logging level | `INFO` | No |
| `JUSTICE_TOOLS_LOG_FILE` | Log file path | - | No |

## Validation Rules

### Process Numbers (CNJ Format)
- Format: `NNNNNNN-DD.AAAA.J.TR.OOOO`
- Supports various input formats with/without separators
- Validates year range (1998-2049) and judicial segments

### Documents
- **CPF**: Format `XXX.XXX.XXX-XX` with digit validation
- **CNPJ**: Format `XX.XXX.XXX/XXXX-XX` with digit validation

## Error Handling

The tools provide comprehensive error handling for:
- Invalid input formats
- API communication errors  
- Authentication failures
- Network timeouts
- Search timeouts (15-minute limit)
- Malformed responses

## Logging

Configurable logging with:
- Console output (always enabled)
- Optional file logging
- Configurable log levels and formats
- Request/response logging for debugging

## Integration with AI Agents

These tools are designed to be called by AI Agents:
1. AI Agent receives user query
2. Tool extracts and validates process/document numbers
3. Tool initiates API search and polls for completion
4. Tool returns structured JSON for AI Agent to process
5. AI Agent generates natural language summary using the JSON data

The tools handle all technical complexity while providing clean, structured data for AI interpretation.