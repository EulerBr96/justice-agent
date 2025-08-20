# Informações do Banco de Dados - Justice Agent

## Dados Atualizados (Obtidos via Heroku CLI)

### Configurações do Banco
- **App Heroku**: `web-justice-db`
- **Add-on**: `postgresql-closed-00241`
- **Plan**: `essential-1`
- **Status**: `Available`
- **PG Version**: `17.4`
- **Criado**: `2025-07-15 16:53`
- **Tamanho dos Dados**: `3.27 GB / 10 GB (32.67%)`
- **Tabelas**: `32/4000`

### Credenciais de Conexão

#### URL Completa
```
postgres://u4hisark730hn2:pc575ba118ece5d11f5f0b30b45d30084ef28de0da28ac9e88d7f4c64ca013346@c80eji844tr0op.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d6rv9lua3u34k3
```

#### Dados Separados
- **Host**: `c80eji844tr0op.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com`
- **Porta**: `5432`
- **Usuário**: `u4hisark730hn2`
- **Senha**: `pc575ba118ece5d11f5f0b30b45d30084ef28de0da28ac9e88d7f4c64ca013346`
- **Database**: `d6rv9lua3u34k3`
- **SSL**: `require`

### Comandos Úteis

#### Para conectar via Heroku CLI
```bash
heroku pg:psql --app web-justice-db
```

#### Para ver configurações
```bash
heroku config --app web-justice-db
```

#### Para ver informações do PostgreSQL
```bash
heroku pg:info --app web-justice-db
```

#### Para ver credenciais
```bash
heroku pg:credentials:url --app web-justice-db
```

### Observações
- O banco está ativo e funcionando
- Há 32 tabelas criadas
- O uso está em 32.67% da capacidade (3.27GB de 10GB)
- A versão do PostgreSQL é 17.4
- O plano é `essential-1` (básico)

### Para usar no código
```python
DATABASE_URL = "postgres://u4hisark730hn2:pc575ba118ece5d11f5f0b30b45d30084ef28de0da28ac9e88d7f4c64ca013346@c80eji844tr0op.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d6rv9lua3u34k3"
```
