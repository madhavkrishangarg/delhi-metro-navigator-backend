import pandas as pd
import pickle
from datetime import datetime, timedelta
from geopy.distance import geodesic
import numpy as np


with open('processed_data.pkl', 'rb') as f:
    (stops_df, routes_df, shapes_df, trips_df, stops_list_df, dict_routes, lines_color_map, routes_trip_map, trip_stop_map, trip_stop_map_translated, list_list_stops, stop_time_map, stop_trip_map) = pickle.load(f)


# with open("shapes_color_mapping.pkl", "rb") as f:
#     shape_color_mapping = pickle.load(f)
    
js_array_str = "const stops_df = {\n"


for index, row in stops_df.iterrows():
    # js_array_str += "{ "
    js_array_str += f"  {row['stop_id']} : {{ stop_name: '{row['stop_name']}', stop_lat: {row['stop_lat']}, stop_lon: {row['stop_lon']} }}, \n"
    # js_array_str += " ,\n"

js_array_str += "};\n\nexport default stops_df;\n"

# print(js_array_str)

# Write the string to a .js file
with open('stops_df.js', 'w') as file:
    file.write(js_array_str)

print("JavaScript file has been created.")