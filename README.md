# Justice Agent

Um agente de IA especializado em consultas e análises de processos judiciais brasileiros, integrado com a API Web Justice.

## 🎯 Sobre o Projeto

O Justice Agent é uma ferramenta inteligente que permite consultar e analisar processos judiciais de forma natural e eficiente. Utiliza técnicas avançadas de processamento de linguagem natural para interpretar consultas em linguagem humana e retornar informações estruturadas sobre processos judiciais.

## 🚀 Funcionalidades

- **Consulta de Processos**: Busca informações detalhadas de processos judiciais
- **Extração de Texto**: Extrai e processa documentos judiciais
- **Análise Inteligente**: Interpreta consultas em linguagem natural
- **Integração com Web Justice**: Conecta-se à API oficial do sistema judiciário
- **Validação de Processos**: Valida números de processo no formato brasileiro
- **Gestão de Tokens**: Gerencia tokens de API de forma eficiente

## 🏗️ Arquitetura

```
justice_agent/
├── agents/           # Agentes de IA especializados
├── api/             # APIs e endpoints
├── config/          # Configurações do sistema
├── db/              # Modelos e migrações de banco
├── tools/           # Ferramentas de consulta e processamento
├── utils/           # Utilitários e helpers
├── workflows/       # Fluxos de trabalho especializados
└── tests/           # Testes automatizados
```

## 🛠️ Tecnologias

- **Python 3.11+**
- **FastAPI** - Framework web para APIs
- **SQLAlchemy** - ORM para banco de dados
- **Redis** - Cache e filas de mensagens
- **PostgreSQL** - Banco de dados principal
- **Claude AI** - Modelo de linguagem para processamento

## 📦 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- PostgreSQL
- Redis
- Conta na API Web Justice

### Configuração

1. **Clone o repositório**:
```bash
git clone https://github.com/seu-usuario/justice-agent.git
cd justice-agent
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. **Execute as migrações**:
```bash
python -m db.migrations
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/justice_agent

# Redis
REDIS_URL=redis://localhost:6379

# Web Justice API
WEB_JUSTICE_API_URL=https://api.webjustice.com.br
WEB_JUSTICE_API_KEY=sua_chave_api

# Claude AI
CLAUDE_API_KEY=sua_chave_claude
```

## 🚀 Uso

### Execução Local

```bash
# Iniciar o agente
python run.sh

# Ou executar diretamente
python simple_agent.py
```

### Uso via API

```bash
# Consultar um processo
curl -X POST "http://localhost:8000/consult" \
  -H "Content-Type: application/json" \
  -d '{"query": "Qual é o status do processo 1234567-89.2023.8.26.0100?"}'
```

## 📚 Documentação

- [Guia de Integração](docs/integration.md)
- [API Reference](docs/api.md)
- [Exemplos de Uso](docs/examples.md)

## 🧪 Testes

```bash
# Executar todos os testes
python -m pytest

# Executar testes específicos
python -m pytest tests/test_agents/
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para suporte e dúvidas:
- Abra uma [issue](https://github.com/seu-usuario/justice-agent/issues)
- Entre em contato: seu-email@exemplo.com

## 🔄 Changelog

### v1.0.0
- Implementação inicial do agente
- Integração com API Web Justice
- Sistema de consulta de processos
- Validação de números de processo
