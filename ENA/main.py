from langchain_ollama import ChatOllama

def Ollama_agent(user_input):
    llm = ChatOllama(model="gemma3:1b")

    SCHEMA = """ Graph Schema:Nodes:- Sample(id, organism, country)- Pathogen(name, resistance)Edges:- Sample -> PathogenAllowed operations:- MATCH- RETURNExample:MATCH (s:Sample)-[:HAS_PATHOGEN]->(p:Pathogen)WHERE p.resistance = "AMR"RETURN s.id, p.name"""

    prompt = f""" Generate a GQL query. Schema: {SCHEMA} Question: {user_input} Output ONLY query."""

    return llm.invoke(prompt).content

def validate_query(query: str) -> bool:
    allowed_keywords = ["MATCH", "RETURN"]
    
    if not all(k in query for k in allowed_keywords):
        return False

    if "DROP" in query or "DELETE" in query:
        return False
    
    return True

def execute_gql(query: str):
    
    mock_db = [
        {"id": "S1", "organism": "E.coli", "country": "India", "pathogen": "E.coli", "resistance": "AMR"},
        {"id": "S2", "organism": "Salmonella", "country": "UK", "pathogen": "Salmonella", "resistance": "None"},
    ]
    if "AMR" in query:
        return [row for row in mock_db if row["resistance"] == "AMR"]

    return mock_db

def format_answer(result):
    if not result:
        return "No data found."

    return "\n".join([str(r) for r in result])


def main():
    print("🔬 ENA Graph Agent (type 'exit' to quit)\n")

    while True:
        user_input = input("Ask: ")

        if user_input.lower() == "exit":
            break

        gql = Ollama_agent(user_input)
        print("\nGenerated GQL:")
        print(gql)

        if not validate_query(gql):
            print("Invalid query")
            continue

        result = execute_gql(gql)
        
        answer = format_answer(result)
        print("\nAnswer:")
        print(answer)


if __name__ == "__main__":
    main()