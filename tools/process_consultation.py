"""
Ferramenta: Consulta de Processo (process_consultation)

Descrição geral
----------------
Esta ferramenta recebe um texto livre do usuário, extrai o primeiro número de processo no padrão CNJ
(ex.: 0000000-00.2020.1.00.0000), inicia uma busca na API Web Justice, realiza polling até a
conclusão e retorna um JSON estruturado com os processos e metadados.

Quando usar
-----------
- Quando o usuário fornecer (ou provavelmente estiver fornecendo) um número de processo em meio ao texto.
- Quando você precisa de um resultado consolidado e detalhado do(s) processo(s) diretamente do banco do sistema.

Quando NÃO usar
----------------
- Se o usuário pediu busca por CPF/CNPJ ou outro documento (use a ferramenta de consulta por documento apropriada).
- Se não há indícios de número de processo no texto (evita inicialização de buscas desnecessárias).

Entrada esperada
----------------
- Texto livre contendo um número de processo no padrão CNJ.
  - A ferramenta faz a extração e normalização automaticamente.

Saída (JSON serializável)
-------------------------
- Em caso de sucesso:
  {
    "status": "success",
    "tool": "process_consultation",
    "query": { "process_number": "...", "search_type": "process" },
    "search_info": { "job_id": "...", "user_id": "...", "user_role": "ai_agent" },
    "data_details": {  # Conteúdo rico retornado pela API
      "total_processos": <int>,
      "documento": "<numero_processo>",
      "user_id": "...",
      "user_role": "...",
      "search_completed_at": "<ISO datetime>",
      "processos": [
        {
          "numero_processo": "...",
          "tribunal": "...",
          "vara": "...",
          "data_distribuicao": "<ISO>",
          "status": "...",
          "status_atual": "...",
          "valor_acao": <float>,
          "polo_ativo": ["..."],
          "polo_passivo": ["..."],
          "movimentos": ["..."],
          "assuntos": ["..."],
          "documentos": [
            {
              "id_documento": <int>,
              "data_juntada": "<ISO>",
              "nome_arquivo": "...",
              "link_texto": "...",
              "sequencia_documento": <int>,
              "id_origem_documento": <int>,
              "hash_documento": "...",
              "texto_extraido": "..."
            }
          ]
        }
      ]
    },
    "summary": {
      "total_processes": <int>,
      "document_searched": "<numero_processo>",
      "search_completed_at": "<ISO datetime>"
    }
  }

- Em caso de erro:
  {
    "status": "error",
    "tool": "process_consultation",
    "error": { "code": "<ERROR_CODE>", "message": "<detalhes>" },
    "data": null
  }

Possíveis códigos de erro (error.code)
--------------------------------------
- "NO_PROCESS_FOUND": não foi possível extrair um número de processo válido do texto.
- "SEARCH_INITIATION_FAILED": a API não retornou job_id ao iniciar a busca.
- "CONSULTATION_ERROR": falha conhecida durante a operação (ex.: polling timeout, erro da API).
- "UNEXPECTED_ERROR": erro inesperado não categorizado.

Pré‑requisitos
--------------
- Variáveis de ambiente:
  - WEB_JUSTICE_API_URL: URL base do API Gateway V2 (ex.: http://localhost:8000).
  - WEB_JUSTICE_API_KEY: chave válida vinculada a um usuário com role "ai_agent".
- Serviços: API Gateway V2 em execução e acessível.

Fluxo interno resumido
----------------------
1) Extrai e normaliza o número de processo (utils.process_validator).
2) Inicia a busca via POST /api/ai-agent/initiate-search (integrations.web_justice_client).
3) Faz polling de status via GET /api/searches/{job_id}/detailed-status até is_ready_for_consultation.
4) Obtém o resultado consolidado via GET /api/ai-agent/processos/{processo}.

Timeouts e robustez
-------------------
- Polling com backoff exponencial (1s → máx. 5s) até ~15 minutos (utils.polling_manager).
- Se exceder o tempo, lança PollingTimeoutError e retorna erro amigável.
- Requisições HTTP com timeouts e tratamento de status code (httpx).

Performance e concorrência
--------------------------
- Polling evita sobrecarga, aumentando o intervalo entre tentativas.
- Não mantém estado global; seguro para múltiplas invocações independentes.

Exemplos de uso
---------------
- Programático:
    from process_consultation import consult_process
    result = consult_process("Preciso do processo 0000000-00.2020.1.00.0000")

- CLI:
    WEB_JUSTICE_API_URL=http://localhost:8000 \
    WEB_JUSTICE_API_KEY=... \
    python3 process_consultation.py "verifique o 0000000-00.2020.1.00.0000"

Limitações conhecidas
---------------------
- Se a API ainda não tiver concluído o job, pode retornar 425 (Too Early) internamente antes da consolidação.
- Campos opcionais podem vir vazios conforme a disponibilidade no banco.

Compatibilidade de resposta
---------------------------
- A ferramenta aceita tanto formatos com "data_details" quanto com "data" vindos da API e normaliza a saída.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import asdict

# Add the tools directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .integrations.web_justice_client import WebJusticeClient, WebJusticeAPIError
from .utils.polling_manager import poll_search_completion, PollingTimeoutError, create_progress_logger
from .utils.process_validator import extract_first_process, ProcessValidationError

# Import Agno tool decorator
from agno.tools import tool

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
            final_response = self._create_success_response(results, process_number, search_response)
            logger.info(f"Final tool response: {json.dumps(final_response, indent=2, ensure_ascii=False)}")
            return final_response
            
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


# Agno tool version
@tool(
    name="consult_legal_process",
    description="Consulta informações de processo judicial usando número de processo CNJ. Extract process numbers from user input and return detailed legal process information including parties, movements, documents, and case status.",
    instructions="Use this tool when the user provides or mentions a legal process number in CNJ format (e.g., 0000000-00.2020.1.00.0000). The tool will automatically extract the process number from the user's message and return comprehensive process information.",
    show_result=False
)
def consult_legal_process_tool(user_input: str) -> Dict[str, Any]:
    """
    Agno tool for consulting legal process information.
    
    Args:
        user_input: User message containing process number
        
    Returns:
        Dict containing process information or error details
    """
    return consult_process(user_input)


if __name__ == "__main__":
    main()