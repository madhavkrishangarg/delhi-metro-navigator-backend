import pandas as pd
import pickle
import matplotlib.pyplot as plt
import requests
from geopy.distance import geodesic

with open('processed_data.pkl', 'rb') as f:
    (stops_df, routes_df, shapes_df, trips_df, stops_list_df, dict_routes, lines_color_map, routes_trip_map, trip_stop_map, trip_stop_map_translated, list_list_stops, stop_time_map, stop_trip_map) = pickle.load(f)


route_shape_mapping = trips_df[['route_id', 'shape_id']].drop_duplicates().groupby('route_id')['shape_id'].apply(list).to_dict()
lines_color_map = {
    "RAPID": "#00B0F0", "AQUA": "#00FFFF", "BLUE": "#0000FF", "GRAY": "#808080", 
    "GREEN": "#008000", "MAGENTA": "#FF00FF", "ORANGE/AIRPORT": "#FFA500", 
    "PINK": "#FFC0CB", "RED": "#FF0000", "VIOLET": "#800080", "YELLOW": "#FFFF00"
}

with open("shapes_color_mapping.pkl", "rb") as f:
    shape_color_mapping = pickle.load(f)
    
print(shape_color_mapping)

# print(shapes_df)

BASE_URL = 'http://127.0.0.1:5500'

start_stop_id = 233  # Replace with a valid stop ID
end_stop_id = 46  # Replace with a valid stop ID
payload = {'start_stop_id': start_stop_id, 'end_stop_id': end_stop_id}
response = requests.post(f"{BASE_URL}/calculate_route", json=payload)
# print(response.json())

for i in response.json():
    shape_id = route_shape_mapping[i['route_id']][0]
    # find the shape_pt_sequence for the from_stop and to_stop
    from_stop_coords = stops_df[stops_df['stop_id'] == i['from_stop']][['stop_lat', 'stop_lon']].values[0]
    to_stop_coords = stops_df[stops_df['stop_id'] == i['to_stop']][['stop_lat', 'stop_lon']].values[0]
    #find the nearest shape_pt to the from_stop and to_stop
    from_stop_shape = shapes_df[shapes_df['shape_id'] == shape_id]
    min_distance = float('inf')
    from_stop_shape_pt = None
    for j, shape in from_stop_shape.iterrows():
        shape_coords = (shape['shape_pt_lat'], shape['shape_pt_lon'])
        distance = geodesic(from_stop_coords, shape_coords).meters
        if distance < min_distance:
            min_distance = distance
            from_stop_shape_pt = shape['shape_pt_sequence']
    to_stop_shape_pt = None
    min_distance = float('inf')
    for j, shape in from_stop_shape.iterrows():
        shape_coords = (shape['shape_pt_lat'], shape['shape_pt_lon'])
        distance = geodesic(to_stop_coords, shape_coords).meters
        if distance < min_distance:
            min_distance = distance
            to_stop_shape_pt = shape['shape_pt_sequence']

    
    # print(from_stop_shape_pt, to_stop_shape_pt, shape_id)
    shape = shapes_df[(shapes_df['shape_id'] == shape_id) & (shapes_df['shape_pt_sequence'] >= from_stop_shape_pt) & (shapes_df['shape_pt_sequence'] <= to_stop_shape_pt)]
    # print(shape)
    plt.plot(shape['shape_pt_lon'], shape['shape_pt_lat'], label=i['route_name'], c = lines_color_map[i['route_name'].split('_')[0]])
    

plt.legend()
plt.show()

# #plot the corresponsing shapes in response using matplotlib
# route_segments = response.json()
# fig, ax = plt.subplots()
# for segment in route_segments:
#     shape_id = route_shape_mapping[segment['route_id']][0]
#     shape = shapes_df[shapes_df['shape_id'] == shape_id]
#     ax.plot(shape['shape_pt_lon'], shape['shape_pt_lat'], label=segment['route_name'])
# ax.legend()
# plt.show()


