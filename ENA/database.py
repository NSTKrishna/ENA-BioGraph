from sqlalchemy import create_engine, inspect, text
import pandas as pd
import random
import string

def generate_random_data(n=1000):
    data = []
    organisms = ["Salmonella", "E. coli", "Klebsiella"]
    countries = ["India", "UK", "Germany", "France"]
    resistance = ["AMR", "Non-AMR"]
    sample = ["Sample A", "Sample B", "Sample C","Sample D", "Sample E", "Sample F","Sample G", "Sample H", "Sample I"]
    for i in range(n):
        data.append({
            "id": i + 1,
            "organism": random.choice(organisms),
            "country": random.choice(countries),
            "resistance": random.choice(resistance),
            "sample": random.choice(sample)
        })
    return pd.DataFrame(data)

def setup_db():
    engine = create_engine("postgresql+psycopg2://postgres:postgres123@localhost:5432/ena_db")

    try:
        inspector = inspect(engine)

        # ✅ Check if table exists
        if "samples" in inspector.get_table_names():
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM samples"))
                count = result.scalar()

                if count > 0:
                    print(f"⚡ Table already seeded with {count} rows. Skipping.")
                    return

        # ✅ If table doesn't exist OR is empty → seed it
        df = generate_random_data(1000)
        print("Generated data:", df.shape)

        # Write core samples table
        df.to_sql(
            "samples",
            engine,
            if_exists="append",   # safe for production
            index=False
        )

        # Write unique lookup tables for Graph Nodes
        df_organisms = pd.DataFrame({"organism": df["organism"].unique()})
        df_organisms.to_sql("organisms", engine, if_exists="replace", index=False)

        df_countries = pd.DataFrame({"country": df["country"].unique()})
        df_countries.to_sql("countries", engine, if_exists="replace", index=False)

        df_resistances = pd.DataFrame({"resistance": df["resistance"].unique()})
        df_resistances.to_sql("resistances", engine, if_exists="replace", index=False)

        print("✅ Seeded PostgreSQL with 1000 rows across unique mapping tables!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    setup_db()