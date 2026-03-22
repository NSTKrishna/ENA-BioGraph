import sqlite3
import random

conn = sqlite3.connect("ena.db")
cursor = conn.cursor()

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS samples (
        id TEXT, 
        organism TEXT, 
        country TEXT, 
        resistance TEXT 
    ) 
""")

organisms = ['E.coli', 'Salmonella', 'K.pneumoniae', 'S.aureus', 'P.aeruginosa']
countries = ['India', 'UK', 'USA', 'Germany', 'Japan', 'Brazil', 'South Africa']
resistances = ['AMR', 'None', 'MDR', 'XDR']

data_to_insert = []
for i in range(1, 101):
    row = (
        f"S{i}", 
        random.choice(organisms), 
        random.choice(countries), 
        random.choice(resistances)
    )
    data_to_insert.append(row)

cursor.executemany("INSERT INTO samples VALUES (?, ?, ?, ?)", data_to_insert)

conn.commit()
print(f"Successfully inserted {len(data_to_insert)} rows into ena.db")
conn.close()
