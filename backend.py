from flask import Flask, request, jsonify
from flask_cors import CORS
import networkx as nx
import pandas as pd
import pickle
import numpy as np
from geopy.distance import geodesic
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

with open('processed_data.pkl', 'rb') as f:
    (stops_df, routes_df, shapes_df, trips_df, stops_list_df, dict_routes, lines_color_map, routes_trip_map, trip_stop_map, trip_stop_map_translated, list_list_stops, stop_time_map, stop_trip_map) = pickle.load(f)

with open('graph.pkl', 'rb') as f:
    G = pickle.load(f)
    
with open('graph_2.pkl', 'rb') as f:
    G_distance = pickle.load(f)

def find_nearest_stop(coords):
    stops_df['distance'] = stops_df.apply(lambda row: geodesic(coords, (row['stop_lat'], row['stop_lon'])).meters, axis=1)
    nearest_stop_id = stops_df.loc[stops_df['distance'].idxmin(), 'stop_id']
    return nearest_stop_id

def get_route_segments(shortest_path, graph):
    route_segments = []
    path_edges = list(zip(shortest_path, shortest_path[1:]))
    route_ids = [graph.get_edge_data(u, v)['route_id'] for u, v in path_edges]

    distance = 0
    distances={}
    for i in range(len(shortest_path)-1):
        distance += graph.get_edge_data(shortest_path[i], shortest_path[i+1])['weight'] 
        distances[shortest_path[i+1]] = distance
    
    route_id_to_name = routes_df.set_index('route_id')['route_long_name'].to_dict()

    current_route_id = route_ids[0]
    current_route_name = route_id_to_name[current_route_id]
    current_route_start, current_route_end = current_route_name.split('_')[1].split(' to ')
    current_route_start = current_route_start.strip()
    current_route_end = current_route_end.strip()
    start_stop = shortest_path[0]

    for i in range(1, len(route_ids)):
        new_route_id = route_ids[i]
        new_route_name = route_id_to_name[new_route_id]
        new_route_start, new_route_end = new_route_name.split('_')[1].split(' to ')
        new_route_start = new_route_start.strip()
        new_route_end = new_route_end.strip()
        if new_route_end != current_route_end:
            end_stop = shortest_path[i]
            route_segments.append({
                'from_stop': int(start_stop),
                'to_stop': int(end_stop),
                'route_name': current_route_name,
                'route_id': int(current_route_id),
                'distance': distances[end_stop],
            })
            current_route_id = route_ids[i]
            current_route_name = route_id_to_name[current_route_id]
            current_route_start, current_route_end = new_route_start, new_route_end
            start_stop = end_stop

    end_stop = shortest_path[-1]
    route_segments.append({
        'from_stop': int(start_stop),
        'to_stop': int(end_stop),
        'route_name': current_route_name,
        'route_id': int(current_route_id),
        'distance': distances[end_stop],
    })

    return route_segments



@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    print('Calculating route request from', request.remote_addr)
    print('Request data:', request.json)
    data = request.json
    try:
        if 'start_stop_id' in data:
            start_stop_id = data['start_stop_id']
        elif 'start_coords' in data:
            start_coords = tuple(data['start_coords'])
            start_stop_id = find_nearest_stop(start_coords)
        else:
            return jsonify({'error': 'Either start_stop_id or start_coords must be provided'}), 400
        
        if 'end_stop_id' in data:
            end_stop_id = data['end_stop_id']
        elif 'end_coords' in data:
            end_coords = tuple(data['end_coords'])
            end_stop_id = find_nearest_stop(end_coords)
        else:
            return jsonify({'error': 'Either end_stop_id or end_coords must be provided'}), 400
        
        if start_stop_id == end_stop_id:
            return jsonify({'error': 'Start and end stops are the same'})
        
        try:
            shortest_path = nx.dijkstra_path(G, source=start_stop_id, target=end_stop_id, weight='weight')
            # print(shortest_path)
            route_segments = get_route_segments(shortest_path, G)
        except nx.NetworkXNoPath:
            return jsonify({'error': f'No path found between stops {start_stop_id} and {end_stop_id}'})

        if(route_segments == []):
            print('No route found')
        return jsonify(route_segments)
    
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 400
    
@app.route('/calculate_route_distance', methods=['POST'])
def calculate_route_distance():
    print('Calculating route request from', request.remote_addr)
    print('Request data:', request.json)
    data = request.json
    try:
        if 'start_stop_id' in data:
            start_stop_id = data['start_stop_id']
        elif 'start_coords' in data:
            start_coords = tuple(data['start_coords'])
            start_stop_id = find_nearest_stop(start_coords)
        else:
            return jsonify({'error': 'Either start_stop_id or start_coords must be provided'}), 400
        
        if 'end_stop_id' in data:
            end_stop_id = data['end_stop_id']
        elif 'end_coords' in data:
            end_coords = tuple(data['end_coords'])
            end_stop_id = find_nearest_stop(end_coords)
        else:
            return jsonify({'error': 'Either end_stop_id or end_coords must be provided'}), 400
        
        if start_stop_id == end_stop_id:
            return jsonify({'error': 'Start and end stops are the same'})
        
        try:
            shortest_path = nx.astar_path(G_distance, start_stop_id, end_stop_id, heuristic=lambda u, v: geodesic((G_distance.nodes[u]['lat'], G_distance.nodes[u]['lon']), (G_distance.nodes[v]['lat'], G_distance.nodes[v]['lon'])).meters, weight='weight')
            # calculate distance
            route_segments = get_route_segments(shortest_path, G_distance)
        except nx.NetworkXNoPath:
            try:
                shortest_path = nx.astar_path(G_distance, start_stop_id, end_stop_id, heuristic=lambda u, v: geodesic((G_distance.nodes[u]['lat'], G_distance.nodes[u]['lon']), (G_distance.nodes[v]['lat'], G_distance.nodes[v]['lon'])).meters, weight='weight')
                route_segments = get_route_segments(shortest_path, G)
            except nx.NetworkXNoPath:
                return jsonify({'error': f'No path found between stops {start_stop_id} and {end_stop_id}'})

        if(route_segments == []):
            print('No route found')
            
        return jsonify(route_segments)
    
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 400
    
@app.route('/find_nearest_stop', methods=['POST'])
def find_nearest_stop_route():
    data = request.json
    try:
        if 'coords' not in data:
            return jsonify({'error': 'Coordinates must be provided'}), 400
        coords = tuple(data['coords'])
        nearest_stop_id = find_nearest_stop(coords)
        nearest_stop_name = stops_df[stops_df['stop_id'] == nearest_stop_id]['stop_name'].values[0]
        return jsonify({'stop_id': nearest_stop_id, 'stop_name': nearest_stop_name})
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 400
    
@app.route('/find_suited_trips', methods=['POST'])
def find_trips():
    data = request.json
    try:
        if 'timestamp' not in data:
            return jsonify({'error': 'Timestamp must be provided'}), 400
        timestamp = data['timestamp']
        
        if 'coords' not in data:
            return jsonify({'error': 'Coordinates must be provided'}), 400
        coords = tuple(data['coords'])
        
        if 'time_window' in data:
            time_window = data['time_window']
        else:
            time_window = 5
        
        if 'accuracy' in data:
            accuracy = data['accuracy']
        else:
            accuracy = 100
        
        if 'previous_suitable_trips' in data:
            previous_suitable_trips = set([int(i) for i in data['previous_suitable_trips']])
        else:
            previous_suitable_trips = None
        
        suitable_trip_routes = find_suitable_trips(timestamp, coords, accuracy, time_window, previous_suitable_trips)
        suitable_trip_routes_str_keys = {str(key): value for key, value in suitable_trip_routes.items()}
        return jsonify(suitable_trip_routes_str_keys)
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 400

def find_suitable_trips(timestamp, coords, accuracy=1000, time_window=4, previous_suitable_trips=None):
    if type(timestamp) == int:
        timestamp = datetime.fromtimestamp(timestamp / 1000)
    else:
        try:
            if ' ' in timestamp:
                timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            else:
                timestamp = datetime.strptime(timestamp, '%H:%M:%S')
        except ValueError:
            raise ValueError("Invalid timestamp format")
    
    time_window_start = timestamp - timedelta(minutes=time_window)
    time_window_end = timestamp + timedelta(minutes=time_window)
    
    closest_stops = []
    for i, stop in stops_df.iterrows():
        stop_coords = (stop['stop_lat'], stop['stop_lon'])
        distance = geodesic(coords, stop_coords).meters
        if distance <= accuracy:
            closest_stops.append(stop['stop_id'])
    
    suitable_trips = set()
    
    for stop_id in closest_stops:
        trips_at_stop = stop_trip_map[stop_id]
        for trip_id in trips_at_stop:
            if previous_suitable_trips and trip_id not in previous_suitable_trips:
                continue
            stop_times = stops_list_df[(stops_list_df['trip_id'] == trip_id) & (stops_list_df['stop_id'] == stop_id)]
            for i, stop_time in stop_times.iterrows():
                arrival_time = datetime.strptime(stop_time['arrival_time'], '%H:%M:%S')
                departure_time = datetime.strptime(stop_time['departure_time'], '%H:%M:%S')
                if time_window_start <= arrival_time <= time_window_end or time_window_start <= departure_time <= time_window_end:
                    suitable_trips.add(trip_id)
    
    suitable_trip_routes = {}
    for trip_id in suitable_trips:
        route_id = trips_df[trips_df['trip_id'] == trip_id]['route_id'].values[0]
        route_name = routes_df[routes_df['route_id'] == route_id]['route_long_name'].values[0]
        suitable_trip_routes[trip_id] = route_name
    
    return suitable_trip_routes

@app.route('/stops', methods=['GET'])
def get_stops():
    try:
        stops_data = stops_df.to_dict(orient='records')
        return jsonify(stops_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# @app.route('/favicon.ico')
# def favicon():
#     return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)
