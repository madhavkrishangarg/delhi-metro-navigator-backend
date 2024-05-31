import pandas as pd
import pickle
import networkx as nx
import matplotlib.pyplot as plt

# Load the processed data
with open('processed_data.pkl', 'rb') as f:
    (stops_df, routes_df, shapes_df, trips_df, stops_list_df, dict_routes, lines_color_map, routes_trip_map, trip_stop_map, trip_stop_map_translated, list_list_stops, stop_time_map, stop_trip_map) = pickle.load(f)

# Initialize a directed graph
G = nx.DiGraph()

# Add nodes (stops)
for _, stop in stops_df.iterrows():
    G.add_node(stop['stop_id'], name=stop['stop_name'], lat=stop['stop_lat'], lon=stop['stop_lon'])

# Add edges based on consecutive stops in trips
for trip_id, stop_ids in trip_stop_map.items():
    for i in range(len(stop_ids) - 1):
        route_id = trips_df[trips_df['trip_id'] == trip_id]['route_id'].values[0]
        G.add_edge(stop_ids[i], stop_ids[i + 1], weight=1, route_id=route_id)

with open('graph.pkl', 'wb') as f:
    pickle.dump(G, f)