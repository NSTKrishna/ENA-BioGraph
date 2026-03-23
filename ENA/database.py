from sqlalchemy import create_engine, inspect, text
import pandas as pd
import random
import string

def generate_random_data(n=1000):
    data = []
    for i in range(n):
        data.append({
            "id": i + 1,
            "name": ''.join(random.choices(string.ascii_letters, k=8)),
            "value": random.randint(1, 1000)
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

        df.to_sql(
            "samples",
            engine,
            if_exists="append",   # safe for production
            index=False
        )

        print("✅ Seeded PostgreSQL with 1000 rows!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    setup_db()