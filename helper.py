import pandas as pd
import pickle
from datetime import datetime, timedelta
from geopy.distance import geodesic
import numpy as np


with open('processed_data.pkl', 'rb') as f:
    (stops_df, routes_df, shapes_df, trips_df, stops_list_df, dict_routes, lines_color_map, routes_trip_map, trip_stop_map, trip_stop_map_translated, list_list_stops, stop_time_map, stop_trip_map) = pickle.load(f)


with open("shapes_color_mapping.pkl", "rb") as f:
    shape_color_mapping = pickle.load(f)
    
js_array_str = "const route_color = [\n"


for key, value in shape_color_mapping.items():
    js_array_str += "  { "
    js_array_str += ", ".join([f"{key}: '{value}'"])
    js_array_str += " },\n"

js_array_str += "];\n\nexport default route_color;\n"

# Write the string to a .js file
with open('route_color.js', 'w') as file:
    file.write(js_array_str)

print("JavaScript file has been created.")