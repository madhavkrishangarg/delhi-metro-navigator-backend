import pandas as pd
import pickle
import networkx as nx
import matplotlib.pyplot as plt


with open('processed_data.pkl', 'rb') as f:
    (stops_df, routes_df, shapes_df, trips_df, stops_list_df, dict_routes, lines_color_map, routes_trip_map, trip_stop_map, trip_stop_map_translated, list_list_stops, stop_time_map, stop_trip_map) = pickle.load(f)

with open('graph.pkl', 'rb') as f:
    G = pickle.load(f)



plt.figure(figsize=(12, 12))
pos = {stop_id: (data['lon'], data['lat']) for stop_id, data in G.nodes(data=True)}
nx.draw(G, pos, with_labels=False, node_size=10, node_color='blue', edge_color='gray', alpha=0.5)
plt.title('Network Graph of Stops')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()


def plot_shortest_route(graph, source_stop_id, target_stop_id):
    try:

        shortest_path = nx.dijkstra_path(graph, source=source_stop_id, target=target_stop_id, weight='weight')
        

        path_positions = {stop_id: (data['lon'], data['lat']) for stop_id, data in graph.nodes(data=True) if stop_id in shortest_path}
        

        path_edges = list(zip(shortest_path, shortest_path[1:]))
        route_ids = [graph.get_edge_data(u, v)['route_id'] for u, v in path_edges]
        

        plt.figure(figsize=(12, 12))
        pos = {stop_id: (data['lon'], data['lat']) for stop_id, data in graph.nodes(data=True)}
        nx.draw(graph, pos, with_labels=False, node_size=10, node_color='blue', edge_color='gray', alpha=0.5)
        

        nx.draw_networkx_nodes(graph, pos, nodelist=shortest_path, node_color='red', node_size=50)
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='red', width=2)
        

        for stop_id in shortest_path:
            stop_name = graph.nodes[stop_id]['name']
            plt.annotate(stop_name, (graph.nodes[stop_id]['lon'], graph.nodes[stop_id]['lat']), textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8, color='red')
        
        plt.title(f'Shortest Route from Stop {source_stop_id} to Stop {target_stop_id}')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid(True)
        plt.show()
        
        print("Routes in the shortest path:")
        current_route_id = route_ids[0]
        current_route_name = routes_df[routes_df['route_id'] == current_route_id]['route_long_name'].values[0]
        start_stop = stops_df[stops_df['stop_id'] == shortest_path[0]]['stop_name'].values[0]
        # start_stop = shortest_path[0]

        for i in range(1, len(route_ids)):
            if route_ids[i] != current_route_id:
                end_stop = stops_df[stops_df['stop_id'] == shortest_path[i]]['stop_name'].values[0]
                print(f"Route from {start_stop} to {end_stop}: {current_route_name}")
                current_route_id = route_ids[i]
                current_route_name = routes_df[routes_df['route_id'] == current_route_id]['route_long_name'].values[0]
                start_stop = stops_df[stops_df['stop_id'] == shortest_path[i]]['stop_name'].values[0]


        print(f"Route from {start_stop} to {shortest_path[-1]}: {current_route_name}")
        
        
    except nx.NetworkXNoPath:
        print(f"No path found between Stop {source_stop_id} and Stop {target_stop_id}")


source_stop_id = 27
target_stop_id = 189


plot_shortest_route(G, source_stop_id, target_stop_id)
