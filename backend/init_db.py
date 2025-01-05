import sqlite3
import pandas as pd

df1 = pd.read_excel("static/nucareCOA.xlsx")
# df2 = pd.read_csv('./data/2020_4NucareTrainingData.csv', encoding='utf-8', header=0)

conn = sqlite3.connect('database.db')

try:
    with open('schema.sql') as f:
        conn.executescript(f.read())     
except FileNotFoundError: 
     print("The file 'schema.sql' was not found.")    
except PermissionError:
    print("Permission denied when trying to read 'schema.sql'.") 
except sqlite3.OperationalError as e: 
    print(f"An operational error occurred: {e}") 
except sqlite3.DatabaseError as e:
    print(f"A database error occurred: {e}") 
except Exception as e: 
    print(f"An unexpected error occurred: {e}")

cur = conn.cursor()

df1.to_sql('nucareCOA', conn, if_exists='replace', index=False)

conn.commit()
conn.close()