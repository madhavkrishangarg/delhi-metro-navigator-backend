import pandas as pd
import pickle
import networkx as nx
import matplotlib.pyplot as plt

with open('processed_data.pkl', 'rb') as f:
    (stops_df, routes_df, shapes_df, trips_df, stops_list_df, dict_routes, lines_color_map, routes_trip_map, trip_stop_map, trip_stop_map_translated, list_list_stops, stop_time_map, stop_trip_map) = pickle.load(f)

with open('updated_routes_df.pkl', 'rb') as f:
    routes_df = pickle.load(f)

G = nx.DiGraph()

for _, stop in stops_df.iterrows():
    G.add_node(stop['stop_id'], name=stop['stop_name'], lat=stop['stop_lat'], lon=stop['stop_lon'])

trip_stop_map_items = list(trip_stop_map.items())
trip_stop_map_items = sorted(trip_stop_map_items, key=lambda x: len(x[1]))

for trip_id, stop_ids in trip_stop_map_items:
    for i in range(len(stop_ids) - 1):
        route_id = trips_df[trips_df['trip_id'] == trip_id]['route_id'].values[0]
        G.add_edge(stop_ids[i], stop_ids[i + 1], weight=1, route_id=route_id)
        
G.add_edge(234, 500, weight=0.0, route_id=16)
G.add_edge(500, 234, weight=0.0, route_id=34)

with open('graph.pkl', 'wb') as f:
    pickle.dump(G, f)