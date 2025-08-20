# AI Agent - Justice Agent

## Project: AI Agent for Lawyers

This is an AI Agent project for lawyers. The agent will help lawyers write, follow up on cases, and understand possible strategies and ways forward.

## Architecture Decisions

- **Dependency Manager**: Use UV as the default package manager.
- **Framework**: Use the Agno Framework for the codebase, with Context7 MCP to consult all documentation.
- **Database**: PostgreSQL with SQLAlchemy as the ORM library.
- **Environment Variables**: All API keys are stored in the `.env` file.
- **Deployment**: The project will be deployed to a VPS using Docker for containerization.

## Recommended Project Structure
```
meu-agente-ia/
├── agents/                    # Definições dos agentes
│   ├── __init__.py
│   ├── analysis_agent.py 
│   ├── research_agent.py 
│   └── models/              # Modelos Pydantic para estruturas de dados
│       ├── __init__.py
│       ├── input_models.py
│       ├── output_models.py
│       └── shared_models.py
├── workflows/               # Workflows e orquestrações
│   ├── __init__.py
│   ├── main_workflow.py
│   └── specialized_flows/
├── tools/                   # Ferramentas customizadas
│   ├── __init__.py
│   ├── custom_tools.py
│   └── integrations/
├── api/                     # Endpoints FastAPI
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── agents.py
│   │   └── workflows.py
│   └── middleware/
├── db/                      # Modelos de banco de dados
│   ├── __init__.py
│   ├── models.py
│   └── migrations/
├── config/                  # Configurações
│   ├── __init__.py
│   ├── settings.py
│   └── environment.py
├── utils/                   # Utilitários compartilhados
│   ├── __init__.py
│   ├── logging.py
│   ├── validation.py
│   └── helpers.py
├── tests/                   # Testes
│   ├── test_agents/
│   ├── test_workflows/
│   └── test_tools/
├── workspace/               # Configuração do workspace Agno
│   ├── dev_resources.py
│   ├── prd_resources.py
│   ├── secrets/
│   └── settings.py
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── CLAUDE.md
└── README.md
```
## Architecture Principles

- **Modular Architecture**: Clear separation between specialized agents, workflows, tools, and APIs, following the structural pattern recommended by Agno.

- **Specialized Agents**: Inheritance-based system that allows creating agents with specific responsibilities (research, analysis, output generation), all using structured outputs with Pydantic.

- **Orchestrated Workflows**: Implementation of workflows that connect multiple agents for complex tasks, leveraging Agno v2's Steps system.

- **Structured Outputs**: Extensive use of Pydantic models to ensure consistency and data validation across all components.

- **Centralized Configuration**: Configuration system that enables easy adaptation between development and production environments.

- **Robust API**: Well-structured FastAPI endpoints for external interaction with the agents.

## Code Style and Patterns

### Anchor Dev Notes

Add specially formatted comments throughout the codebase, where appropriate, for yourself as inline knowledge that can be easily `grep`ped for.

### Guidelines

- Use `AIDEV-NOTE:`, `AIDEV-TODO:`, or `AIDEV-QUESTION:` (all-caps prefix) for comments aimed at AI and developers.
- Keep them concise (≤ 120 characters).
- **Important:** Before scanning files, always first try to **locate existing anchors** `AIDEV-*` in relevant subdirectories.
- **Update relevant anchors** when modifying associated code.
- **Do not remove `AIDEV-NOTE`s** without explicit human instruction.
- Make sure to add relevant anchor comments whenever a file or piece of code is:
  - Too complex, or
  - Very important, or
  - Confusing, or
  - Could have a bug

### Example

```python
# AIDEV-NOTE: perf-hot-path; avoid extra allocations (see ADR-24)
async def render_feed(...):
    ...