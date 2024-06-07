import pandas as pd
import pickle
import networkx as nx
import matplotlib.pyplot as plt

# Load the processed data
with open('processed_data.pkl', 'rb') as f:
    (stops_df, routes_df, shapes_df, trips_df, stops_list_df, dict_routes, lines_color_map, routes_trip_map, trip_stop_map, trip_stop_map_translated, list_list_stops, stop_time_map, stop_trip_map) = pickle.load(f)
    
with open("../raw-data/trip_stop_map_translated.txt", "r") as f:
    data = f.read()
    
#add a columns of starting_point to routes_df by extracting starting point from routes_df['route_long_name].split('_')[1].split(" to ")[0].strip()
routes_df['start_point'] = routes_df['route_long_name'].map(lambda x: x.split('_')[1].split(" to ")[0].strip())
routes_df['end_point'] = routes_df['route_long_name'].map(lambda x: x.split('_')[1].split(" to ")[1].strip())

data = data.split("\n")

data2 = []

for i in data:
    temp = [j.strip() for j in i.split("->") if j != ""]
    if temp != []:
        data2.append(temp)

# print(data2)

for i in data2:
    for j in range(len(routes_df)):
        if i[0] == routes_df["start_point"].iloc[j] and i[-1] == routes_df["end_point"].iloc[j]:
            #add column no_of_stops to routes_df
            routes_df.loc[j, "no_of_stops"] = len(i)
            
with open("updated_routes_df.pkl", "wb") as f:
    pickle.dump(routes_df, f)
    
# trip_stop_map_items = list(trip_stop_map.items())

# #sort the trip_stop_map_items by the length of the value of each item
# trip_stop_map_items = sorted(trip_stop_map_items, key=lambda x: len(x[1]))
# for trip_id, stop_ids in trip_stop_map_items:
#     print(trip_id, stop_ids)

# with open('updated_routes_df.pkl', 'rb') as f:
#     routes_df = pickle.load(f)