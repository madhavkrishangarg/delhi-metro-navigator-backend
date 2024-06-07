import pandas as pd
import pickle
import networkx as nx
import matplotlib.pyplot as plt

# Load the processed data
with open('processed_data.pkl', 'rb') as f:
    (stops_df, routes_df, shapes_df, trips_df, stops_list_df, dict_routes, lines_color_map, routes_trip_map, trip_stop_map, trip_stop_map_translated, list_list_stops, stop_time_map, stop_trip_map) = pickle.load(f)

with open('updated_routes_df.pkl', 'rb') as f:
    routes_df = pickle.load(f)
    
#print all headers of stops_list_df
print(stops_list_df.columns)

# Initialize a directed graph
G_distance = nx.DiGraph()

# Add nodes (stops)
for _, stop in stops_df.iterrows():
    G_distance.add_node(stop['stop_id'], name=stop['stop_name'], lat=stop['stop_lat'], lon=stop['stop_lon'])

# print(stop_time_map)
trip_stop_map_items = list(trip_stop_map.items())
trip_stop_map_items = sorted(trip_stop_map_items, key=lambda x: len(x[1]))

# Add edges based on consecutive stops in trips
for trip_id, stop_ids in trip_stop_map.items():
    for i in range(len(stop_ids) - 1):
        route_id = trips_df[trips_df['trip_id'] == trip_id]['route_id'].values[0]
        stop_1_condition = (stops_list_df['trip_id'] == trip_id) & (stops_list_df['stop_id'] == stop_ids[i])
        stop_2_condition = (stops_list_df['trip_id'] == trip_id) & (stops_list_df['stop_id'] == stop_ids[i + 1])
        distance = stops_list_df[stop_2_condition]['shape_dist_traveled'].values[0] - stops_list_df[stop_1_condition]['shape_dist_traveled'].values[0]
        # print(distance)
        G_distance.add_edge(stop_ids[i], stop_ids[i + 1], weight=distance, route_id=route_id)
    
G_distance.add_edge(234, 500, weight=0.0, route_id=16)
G_distance.add_edge(500, 234, weight=0.0, route_id=34)

with open('graph_2.pkl', 'wb') as f:
    pickle.dump(G_distance, f)
