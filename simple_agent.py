from agno.agent import Agent
from agno.models.groq import Groq
from agno.storage.postgres import PostgresStorage
from dotenv import load_dotenv

load_dotenv()

db = PostgresStorage(
    table_name="agent_session",
    schema="ai",
    db_url="postgresql://u4hisark730hn2:pc575ba118ece5d11f5f0b30b45d30084ef28de0da28ac9e88d7f4c64ca013346@c80eji844tr0op.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d6rv9lua3u34k3",
    auto_upgrade_schema=True
)

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    name="Justice Agent",
    storage=db,
    add_history_to_messages=True,
    num_history_runs=3
)

if __name__ == "__main__":
    print("🤖 Justice Agent iniciado!")
    print("Digite 'sair' para encerrar")
    
    while True:
        try:
            user_input = input("\n💬 Você: ")
            if user_input.lower() == 'sair':
                print("👋 Até logo!")
                break
            
            print("🤔 Processando...")
            response = agent.run(user_input)
            print(f"🤖 Justice Agent: {response.content}")
            
        except KeyboardInterrupt:
            print("\n👋 Encerrando...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
