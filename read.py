#read from stops_data.db

import sqlite3
import pandas as pd

conn = sqlite3.connect('stops_data.db')
stops_df = pd.read_sql_query("SELECT * FROM stops", conn)   
print(stops_df)