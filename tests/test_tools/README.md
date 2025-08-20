# Justice Agent API Simulation Tests

Este diretório contém testes para simular chamadas de API do AI Agent, permitindo monitorar os logs nos containers Docker locais.

## Arquivos

- **`test_basic_connectivity.py`** - Teste básico de conectividade e importação das ferramentas
- **`test_api_simulation.py`** - Simulação completa das chamadas de API do agente
- **`README.md`** - Este arquivo de documentação

## Pré-requisitos

1. **Ambiente configurado**:
   ```bash
   export WEB_JUSTICE_API_KEY="sua_chave_api_aqui"
   export WEB_JUSTICE_API_URL="http://localhost:8000"  # opcional
   ```

2. **Containers Docker rodando**:
   ```bash
   cd /path/to/web-justice-v0
   docker-compose up -d
   ```

3. **Dependências instaladas**:
   ```bash
   cd /path/to/justice_agent/tools
   pip install -r requirements.txt
   ```

## Como usar

### 1. Teste básico de conectividade

Execute primeiro para verificar se tudo está configurado:

```bash
cd /Users/viniciusroncon/Documents/apps/justice_agent/tests/test_tools
python test_basic_connectivity.py
```

Este teste verifica:
- ✅ Configuração do ambiente (API key)
- ✅ Importação das ferramentas
- ✅ Conectividade com a API
- ✅ Autenticação
- ✅ Health check

### 2. Simulação completa da API

Execute para simular chamadas reais do AI Agent:

```bash
python test_api_simulation.py
```

Este teste realiza:
- 🔍 Consulta por número de processo
- 👤 Consulta por CPF
- 🏢 Consulta por CNPJ  
- 🔄 Múltiplas consultas sequenciais

## Monitoramento dos Logs

Durante a execução dos testes, monitore os workers AI em terminais separados:

```bash
# Worker de buscas AI
docker-compose logs -f worker-ai-searches

# Worker de detalhes AI
docker-compose logs -f worker-ai-details

# Worker de documentos AI
docker-compose logs -f worker-ai-documents

# Ver status de todos os serviços
docker-compose ps
```

## Estrutura dos Testes

### Fluxo completo testado:

1. **Inicialização**: Tool recebe input do usuário
2. **Validação**: Extrai e valida número de processo/documento
3. **API Call**: Chama `/api/ai-agent/initiate-search`
4. **Queue**: Task é enviada para fila AI apropriada
5. **Worker**: Worker AI processa a task
6. **Integration**: Worker chama ferramentas do justice_agent
7. **Polling**: Tool faz polling do status da busca
8. **Results**: Tool recupera resultados finais
9. **Response**: Retorna JSON estruturado para o LLM

### Workers testados:

- **worker-ai-searches** - Processa buscas por documento (CPF/CNPJ)
- **worker-ai-details** - Processa detalhes de processos específicos
- **worker-ai-documents** - Extrai documentos (futuro uso)

## Arquivos de Log

Os testes geram arquivos de log detalhados:
- `test_api_simulation_YYYYMMDD_HHMMSS.log` - Log completo da simulação

## Resolução de Problemas

### Erro: "WEB_JUSTICE_API_KEY not set"
```bash
export WEB_JUSTICE_API_KEY="sua_chave_api_aqui"
```

### Erro: "Connection refused"
Verifique se os containers estão rodando:
```bash
docker-compose ps
docker-compose up -d
```

### Erro: "Authentication failed"
Verifique se a API key está correta e válida.

### Workers não processam tasks
Verifique se os novos workers AI estão rodando:
```bash
docker-compose logs worker-ai-searches
docker-compose logs worker-ai-details
docker-compose logs worker-ai-documents
```

## Observações

- Os testes usam números de processo e documentos fictícios
- É normal que as buscas retornem "não encontrado" 
- O importante é verificar se todo o fluxo funciona
- Os workers AI devem mostrar logs de atividade
- As ferramentas do justice_agent devem ser chamadas pelos workers

## Comandos úteis

```bash
# Ver todos os logs em tempo real
docker-compose logs -f

# Reiniciar apenas os workers AI
docker-compose restart worker-ai-searches worker-ai-details worker-ai-documents

# Ver status detalhado dos containers
docker-compose ps --format "table {{.Name}}\t{{.Command}}\t{{.RunningFor}}\t{{.Status}}\t{{.Ports}}"
```