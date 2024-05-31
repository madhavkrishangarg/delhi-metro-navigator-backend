import pandas as pd
import sqlite3

stops_df = pd.read_csv("stops.txt")
stops_df = stops_df.dropna(axis=1, how='all')

# print(stops_df)

conn = sqlite3.connect('stops_data.db')
cursor = conn.cursor()

# Write the DataFrame to SQLite database
stops_df.to_sql('stops', conn, if_exists='replace', index=False)

# Commit changes and close connection
conn.commit()
conn.close()
