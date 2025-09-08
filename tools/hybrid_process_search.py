"""
Tool Híbrida para Busca de Processos: RAG + API Fallback
=========================================================

Esta tool implementa uma estratégia híbrida:
1. Primeira tentativa: Busca RAG no banco vetorial (instantânea)
2. Fallback: Se não encontrar → API externa (com notificação por e-mail)

Combina a velocidade do RAG local com a cobertura completa da API.
"""

import logging
from typing import Dict, Any, List, Optional
from agno import Tool

# Import da tool existente para fallback
from justice_agent.tools.integrations.web_justice_client import WebJusticeClient
from justice_agent.tools.process_consultation import ProcessConsultationTool

logger = logging.getLogger(__name__)

class HybridProcessSearchTool(Tool):
    """
    Tool híbrida que combina busca RAG com fallback para API externa.
    
    Fluxo de operação:
    1. Busca no banco vetorial local (RAG) - instantânea
    2. Se não encontrar resultados relevantes → Busca via API
    3. Para buscas via API → Resposta com promessa de e-mail
    """
    
    def __init__(self):
        super().__init__(
            name="hybrid_process_search",
            description="Busca híbrida de processos: RAG local + API externa com notificação por e-mail"
        )
        
        # Inicializar clientes
        self.web_client = None
        self.process_tool = None
        self.vector_client = None
        
        # Tentar inicializar componentes (não falhar se indisponíveis)
        try:
            self.web_client = WebJusticeClient()
            logger.info("✅ WebJusticeClient inicializado")
        except Exception as e:
            logger.warning(f"⚠️ WebJusticeClient indisponível: {e}")
        
        try:
            self.process_tool = ProcessConsultationTool()
            logger.info("✅ ProcessConsultationTool inicializado")
        except Exception as e:
            logger.warning(f"⚠️ ProcessConsultationTool indisponível: {e}")
        
        # Cliente vetorial (importar localmente para evitar dependências circulares)
        self._init_vector_client()
    
    def _init_vector_client(self):
        """Inicializa cliente vetorial com tratamento de erros."""
        try:
            # Import local para evitar problemas de dependência
            import sys
            import os
            sys.path.append('/Users/viniciusroncon/Documents/apps/web-justice-v0')
            
            from shared.vector_client import get_vector_client
            self.vector_client = get_vector_client()
            
            if self.vector_client.is_enabled():
                logger.info("✅ Cliente vetorial RAG inicializado")
            else:
                logger.info("🚫 Cliente vetorial desabilitado")
                
        except Exception as e:
            logger.warning(f"⚠️ Cliente vetorial indisponível: {e}")
            self.vector_client = None
    
    def _search_via_rag(self, query: str, numero_processo: str = None) -> List[Dict[str, Any]]:
        """
        Busca usando RAG (banco vetorial).
        
        Args:
            query: Consulta em linguagem natural
            numero_processo: Número do processo específico (opcional)
            
        Returns:
            Lista de documentos encontrados via RAG
        """
        if not self.vector_client or not self.vector_client.is_enabled():
            logger.debug("Cliente vetorial não disponível para busca RAG")
            return []
        
        try:
            logger.info(f"🔍 [RAG] Buscando: '{query[:50]}...'")
            
            # Busca por número de processo específico
            if numero_processo:
                results = self.vector_client.search_by_process_number(
                    numero_processo=numero_processo,
                    limit=10
                )
            else:
                # Busca semântica geral
                results = self.vector_client.search_similar_documents(
                    query=query,
                    limit=5
                )
            
            if results:
                logger.info(f"✅ [RAG] Encontrados {len(results)} documentos")
                return results
            else:
                logger.info("🔍 [RAG] Nenhum documento encontrado")
                return []
                
        except Exception as e:
            logger.error(f"❌ [RAG] Erro na busca vetorial: {e}")
            return []
    
    def _format_rag_response(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Formata resposta da busca RAG para o agente.
        
        Args:
            results: Resultados da busca vetorial
            
        Returns:
            Resposta formatada para o agente
        """
        if not results:
            return {
                "status": "no_results",
                "source": "rag",
                "message": "Nenhum documento encontrado na base local."
            }
        
        # Agrupar por processo
        processes = {}
        for doc in results:
            proc_num = doc.get("numero_processo", "Processo não identificado")
            if proc_num not in processes:
                processes[proc_num] = {
                    "numero_processo": proc_num,
                    "id_processo": doc.get("id_processo"),
                    "documentos": [],
                    "score_maximo": 0
                }
            
            processes[proc_num]["documentos"].append({
                "conteudo": doc.get("content", "")[:500] + "..." if len(doc.get("content", "")) > 500 else doc.get("content", ""),
                "tipo_documento": doc.get("metadata", {}).get("tipo_documento"),
                "data_juntada": doc.get("metadata", {}).get("data_juntada"),
                "score_similaridade": doc.get("score", 0)
            })
            
            # Atualizar score máximo
            processes[proc_num]["score_maximo"] = max(
                processes[proc_num]["score_maximo"], 
                doc.get("score", 0)
            )
        
        # Ordenar por relevância
        sorted_processes = sorted(
            processes.values(), 
            key=lambda x: x["score_maximo"], 
            reverse=True
        )
        
        return {
            "status": "success",
            "source": "rag",
            "message": f"Encontrados {len(sorted_processes)} processos relevantes na base local.",
            "total_processos": len(sorted_processes),
            "total_documentos": len(results),
            "processos": sorted_processes[:3],  # Limitar a 3 processos mais relevantes
            "observacao": "Resultados obtidos instantaneamente via busca semântica (RAG)."
        }
    
    def _initiate_api_search(self, document_or_process: str) -> Dict[str, Any]:
        """
        Inicia busca via API externa como fallback.
        
        Args:
            document_or_process: Documento ou processo para buscar
            
        Returns:
            Resposta com informações do job iniciado
        """
        if not self.web_client:
            return {
                "status": "error",
                "message": "Cliente da API externa não está disponível."
            }
        
        try:
            logger.info(f"🌐 [API] Iniciando busca externa para: {document_or_process}")
            
            # Usar a tool existente para iniciar busca
            api_response = self.web_client.initiate_search(
                document=document_or_process,
                search_type="document"  # ou "process" dependendo do contexto
            )
            
            logger.info(f"✅ [API] Busca iniciada - Job ID: {api_response.get('job_id')}")
            
            return {
                "status": "search_initiated",
                "source": "api_external",
                "job_id": api_response.get('job_id'),
                "message": "Busca iniciada via API externa.",
                "estimated_time": "5-10 minutos"
            }
            
        except Exception as e:
            logger.error(f"❌ [API] Erro ao iniciar busca: {e}")
            return {
                "status": "error",
                "source": "api_external", 
                "message": f"Erro ao iniciar busca via API: {str(e)}"
            }
    
    def run(self, query: str, numero_processo: str = None) -> str:
        """
        Executa busca híbrida: RAG first, API fallback.
        
        Args:
            query: Consulta do usuário sobre processo
            numero_processo: Número específico do processo (opcional)
            
        Returns:
            Resposta formatada para o usuário
        """
        logger.info(f"🚀 [HYBRID] Iniciando busca híbrida para: '{query[:100]}...'")
        
        # ETAPA 1: Tentativa RAG (busca vetorial local)
        rag_results = self._search_via_rag(query, numero_processo)
        
        if rag_results:
            # RAG encontrou resultados - retornar imediatamente
            rag_response = self._format_rag_response(rag_results)
            
            response_text = f"""
📊 **Resultados encontrados na base local (RAG)**

{rag_response['message']}

**Processos relevantes:**
"""
            
            for i, processo in enumerate(rag_response.get('processos', [])[:3], 1):
                response_text += f"""
{i}. **Processo:** {processo['numero_processo']}
   - **Documentos:** {len(processo['documentos'])} documento(s)
   - **Relevância:** {processo['score_maximo']:.2f}
   
"""
                
                # Mostrar alguns documentos
                for doc in processo['documentos'][:2]:
                    response_text += f"   • {doc.get('tipo_documento', 'Documento')}: {doc.get('conteudo', 'Conteúdo não disponível')}\n"
                    if doc.get('data_juntada'):
                        response_text += f"     Data: {doc['data_juntada']}\n"
                response_text += "\n"
            
            response_text += "\n✅ *Busca realizada instantaneamente via sistema RAG.*"
            return response_text
        
        # ETAPA 2: Fallback para API externa
        logger.info("🌐 [HYBRID] RAG não retornou resultados, iniciando fallback via API")
        
        # Determinar termo de busca
        search_term = numero_processo if numero_processo else query
        
        api_response = self._initiate_api_search(search_term)
        
        if api_response['status'] == 'search_initiated':
            response_text = f"""
🔍 **Busca não encontrada na base local**

Os termos buscados não foram encontrados em nossa base de dados local. 

**Iniciando busca na base externa:**
- **Status:** Busca em andamento
- **ID do Job:** {api_response.get('job_id', 'N/A')}
- **Tempo estimado:** {api_response.get('estimated_time', 'Indeterminado')}

📧 **Você será notificado por e-mail quando a busca for concluída.**

⏰ A busca externa pode levar alguns minutos para processar todos os tribunais e sistemas.
"""
        else:
            response_text = f"""
❌ **Erro na busca**

Não foi possível encontrar resultados na base local nem iniciar busca externa.

**Detalhes do erro:**
{api_response.get('message', 'Erro não especificado')}

💡 **Sugestões:**
- Verifique se o número do processo está correto
- Tente termos de busca diferentes
- Entre em contato com o suporte se o problema persistir
"""
        
        return response_text


# Instanciar a tool para uso pelo agente
hybrid_process_search = HybridProcessSearchTool()