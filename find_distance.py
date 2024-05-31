import pandas as pd
import pickle
from datetime import datetime, timedelta
from geopy.distance import geodesic
import numpy as np


with open('processed_data.pkl', 'rb') as f:
    (stops_df, routes_df, shapes_df, trips_df, stops_list_df, dict_routes, lines_color_map, routes_trip_map, trip_stop_map, trip_stop_map_translated, list_list_stops, stop_time_map, stop_trip_map) = pickle.load(f)




def find_suitable_trips(timestamp, coords, accuracy=1000, time_window=4, previous_suitable_trips=None):
    print(previous_suitable_trips)
    if type(timestamp) == int:
        # Assuming timestamp is in milliseconds
        timestamp = datetime.fromtimestamp(timestamp / 1000)
    else:
        try:
            if 'T' in timestamp:
                timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
            elif ' ' in timestamp:
                timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            else:
                # Assuming only time is provided
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
    
    print(f'Closest stops within {accuracy} meters: {closest_stops}')
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

# timestamp_1 = '08:30:00'
# coords_1 = (28.570086115221535, 77.33277393245963)
# suitable_trip_routes_1 = find_suitable_trips(timestamp_1, coords_1)
# print(f'Suitable trips for timestamp {timestamp_1} and coordinates {coords_1}:')
# for trip_id, route_name in suitable_trip_routes_1.items():
#     print(f'Trip ID: {trip_id}, Route: {route_name}')
# print("\n")

# # Use previously suitable trips for the next calculation
# previous_suitable_trips = set(suitable_trip_routes_1.keys())

# timestamp_2 = '08:33:00'
# coords_2 = (28.5731098057556, 77.32486528281848)
# suitable_trip_routes_2 = find_suitable_trips(timestamp_2, coords_2, previous_suitable_trips=previous_suitable_trips)
# print(f'Suitable trips for timestamp {timestamp_2} and coordinates {coords_2}:')
# for trip_id, route_name in suitable_trip_routes_2.items():
#     print(f'Trip ID: {trip_id}, Route: {route_name}')
# print("\n")

# timestamp_3 = '02:00:00'
# coords_3 = (28.7041, 77.1025)
# suitable_trip_routes_3 = find_suitable_trips(timestamp_3, coords_3)
# print(f'Suitable trips for timestamp {timestamp_3} and coordinates {coords_3}:')
# for trip_id, route_name in suitable_trip_routes_3.items():
#     print(f'Trip ID: {trip_id}, Route: {route_name}')
# print("\n")

# timestamp_4 = '09:00:00'
# coords_4 = (28.6200, 77.3800)
# accuracy_4 = 2000
# suitable_trip_routes_4 = find_suitable_trips(timestamp_4, coords_4, accuracy=accuracy_4)
# print(f'Suitable trips for timestamp {timestamp_4}, coordinates {coords_4}, and accuracy {accuracy_4} meters:')
# for trip_id, route_name in suitable_trip_routes_4.items():
#     print(f'Trip ID: {trip_id}, Route: {route_name}')
# print("\n")

# timestamp_5 = '10:00:00'
# coords_5 = (28.5900, 77.2900)
# time_window_5 = 10
# suitable_trip_routes_5 = find_suitable_trips(timestamp_5, coords_5, time_window=time_window_5)
# print(f'Suitable trips for timestamp {timestamp_5}, coordinates {coords_5}, and time window ±{time_window_5} minutes:')
# for trip_id, route_name in suitable_trip_routes_5.items():
#     print(f'Trip ID: {trip_id}, Route: {route_name}')
# print("\n")


timestamp_6 = '20:37:00'
coords_6 = (28.549532,77.258789)
suitable_trip_routes_6 = find_suitable_trips(timestamp_6, coords_6, accuracy=500, time_window=1)
print(f'Suitable trips for timestamp {timestamp_6} and coordinates {coords_6}:')
for trip_id, route_name in suitable_trip_routes_6.items():
    print(f'Trip ID: {trip_id}, Route: {route_name}')
print("\n")

timestamp_7 = '20:39:00'
coords_7 = (28.544413,77.264259)
suitable_trip_routes_7 = find_suitable_trips(timestamp_7, coords_7, previous_suitable_trips=set(suitable_trip_routes_6.keys()), accuracy=500, time_window=1)
print(f'Suitable trips for timestamp {timestamp_7} and coordinates {coords_7}:')
for trip_id, route_name in suitable_trip_routes_7.items():
    print(f'Trip ID: {trip_id}, Route: {route_name}')
