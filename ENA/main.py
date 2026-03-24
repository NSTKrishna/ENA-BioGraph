from langchain_ollama import ChatOllama
from gremlin_python.driver import client, serializer
import re

llm = ChatOllama(model="gemma3:1b", temperature=0)


def connect():
    return client.Client(
        "ws://localhost:8182/gremlin",
        "g",
        message_serializer=serializer.GraphSONSerializersV3d0()
    )


# ---------------- STRICT PROMPT ----------------

def generate_query(question):
    prompt = f"""
You are a STRICT Gremlin generator.

Graph Schema:
(sample)-[:HAS_COUNTRY]->(country)
(sample)-[:HAS_ORGANISM]->(organism)
(sample)-[:HAS_RESISTANCE]->(resistance)

Rules:
- ONLY output Gremlin
- Strictly follow this valueMap() MUST ALWAYS be the LAST step
- ALWAYS start with g.V()
- ALWAYS use hasLabel('sample') (lowercase)
- NEVER use has('country',...) directly on sample
- ALWAYS traverse edges using out()
- Allowed filters:
    country → out('HAS_COUNTRY').has('country', VALUE)
    organism → out('HAS_ORGANISM').has('organism', VALUE)
    resistance → out('HAS_RESISTANCE').has('resistance', VALUE)
- NEVER explain

Examples:

g.V().hasLabel('sample')
  .where(out('HAS_COUNTRY').has('country', 'India'))

g.V().hasLabel('sample')
  .where(out('HAS_COUNTRY').has('country', 'India'))
  .where(out('HAS_ORGANISM').has('organism', 'Salmonella'))
  .where(out('HAS_RESISTANCE').has('resistance', 'AMR'))
  .valueMap()

User: {question}
"""
    return llm.invoke(prompt).content.strip()


# ---------------- SAFETY ----------------

def clean_query(text):
    text = re.sub(r'```.*?\n', '', text, flags=re.DOTALL).strip()

    if "g.V()" in text:
        return text[text.index("g.V()"):].strip()

    return None

def fallback(q):
    q = q.lower()

    query = "g.V().hasLabel('sample')"

    filters = []

    if "india" in q:
        filters.append("out('HAS_COUNTRY').has('country','India')")

    if "salmonella" in q:
        filters.append("out('HAS_ORGANISM').has('organism','Salmonella')")

    if "amr" in q:
        filters.append("out('HAS_RESISTANCE').has('resistance','AMR')")

    if filters:
        query += ".and(" + ", ".join(filters) + ")"

    return query + ".valueMap()"


def validate(q):
    return (
        q.startswith("g.V()")
        and "drop" not in q.lower()
        and "hasLabel('sample')" in q
    )


# ---------------- EXECUTION ----------------

def run(graph, query):
    return graph.submit(query).all().result()


# ---------------- MAIN ----------------

def main():
    graph = connect()

    while True:
        q = input("Ask: ")

        if q.lower() == "exit":
            break
        raw = generate_query(q)
        gremlin = clean_query(raw) or fallback(q)

        if not validate(gremlin):
            print("❌ Invalid query")
            continue

        print("🔍", gremlin)

        result = run(graph, gremlin)

        for r in result:
            print(f"[{r['id']}] {r['organism']} | {r['country']} | {r['resistance']} | {r['sample']}")


if __name__ == "__main__":
    main()