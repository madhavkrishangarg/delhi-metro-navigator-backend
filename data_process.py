import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pickle

# Load the data
stops_df = pd.read_csv("stops.txt")
routes_df = pd.read_csv("routes.txt")
shapes_df = pd.read_csv("shapes.txt")
trips_df = pd.read_csv("trips.txt")
stops_list_df = pd.read_csv("stop_times.txt")

def correct_timestamp(ts):
    ts_parts = ts.split(':')
    hours = int(ts_parts[0])
    if hours >= 24:
        hours -= 24
        ts_parts[0] = f"{hours:02}"
        # print(f"Corrected timestamp: {ts} -> {':'.join(ts_parts)}")
    return ":".join(ts_parts)

# Apply the timestamp correction
stops_list_df['arrival_time'] = stops_list_df['arrival_time'].apply(correct_timestamp)
stops_list_df['departure_time'] = stops_list_df['departure_time'].apply(correct_timestamp)


# Process the data as in your script
routes_df['route_name'] = routes_df['route_long_name'].str.split('_').str[0]
routes = routes_df['route_name'].unique()

stops_df = stops_df.dropna(axis=1, how='all')
routes_df = routes_df.dropna(axis=1, how='all')
shapes_df = shapes_df.dropna(axis=1, how='all')
trips_df = trips_df.dropna(axis=1, how='all')
stops_list_df = stops_list_df.dropna(axis=1, how='all')


dict_routes = {}
for i in routes:
    if(dict_routes.get(i) == None):
        dict_routes[i] = []
    route_id = routes_df[routes_df['route_name'] == i]['route_id'].values
    for j in route_id:
        shape_id = trips_df[trips_df['route_id'] == j]['shape_id'].values[0]
        dict_routes[i].append(shape_id)
    
lines_color_map = {
    "RAPID": "#00B0F0", "AQUA": "#00FFFF", "BLUE": "#0000FF", "GRAY": "#808080", 
    "GREEN": "#008000", "MAGENTA": "#FF00FF", "ORANGE/AIRPORT": "#FFA500", 
    "PINK": "#FFC0CB", "RED": "#FF0000", "VIOLET": "#800080", "YELLOW": "#FFFF00"
}

routes_trip_map = {}

for i in range(len(routes_df)):
    tup = (routes_df['route_id'][i], routes_df['route_long_name'][i])
    if(routes_trip_map.get(tup) == None):
        routes_trip_map[tup] = []
    
    r_id = tup[0]
    for j in range(len(trips_df)):
        if(trips_df['route_id'][j] == r_id):
            routes_trip_map[tup].append(trips_df['trip_id'][j])

plt.figure(figsize=(12, 12))

for i in dict_routes:
    for j in dict_routes[i]:
        shape = shapes_df[shapes_df['shape_id'] == j]
        plt.plot(shape['shape_pt_lon'], shape['shape_pt_lat'], c=lines_color_map[i], label=i)


plt.title('Transit Shapes, Stops, and Routes')
plt.xlabel('Longitude')
plt.ylabel('Latitude')


legend = []
for i in lines_color_map:
    legend.append(plt.Line2D([0], [0], color=lines_color_map[i], lw=4, label=i))
plt.legend(handles=legend, title='Routes', loc='best')

plt.grid(True)
# plt.show()

trip_ids = trips_df['trip_id'].unique()

#create a list of stop_ids for each trip_id sorted by stop_sequence
trip_stop_map = {}
for i in trip_ids:
    trip_stop_map[i] = []
    stops = stops_list_df[stops_list_df['trip_id'] == i]
    stops = stops.sort_values(by='stop_sequence')
    for j in range(len(stops)):
        trip_stop_map[i].append(stops['stop_id'].values[j])

    
trip_stop_map_translated = {}  
for i in trip_stop_map.items():
    if(trip_stop_map_translated.get(tuple(i[1])) == None):
        trip_stop_map_translated[tuple(i[1])] = []
    trip_stop_map_translated[tuple(i[1])].append(i[0])
    
    
list_list_stops = []
for i in trip_stop_map:
    list_stops = []
    for j in trip_stop_map[i]:
        stop = stops_df[stops_df['stop_id'] == j]
        list_stops.append((stop['stop_name'].values[0]))
    list_list_stops.append(list_stops)
    
    
stop_time_map = {}
for i in stops_list_df['stop_id']:
    stop_time_map[i] = []
    stop_times = stops_list_df[stops_list_df['stop_id'] == i]
    for j in range(len(stop_times)):
        stop_time_map[i].append(stop_times['arrival_time'].values[j])


stop_trip_map = {}
for i in stops_list_df['stop_id']:
    stop_trip_map[i] = []
    t_id = stops_list_df[stops_list_df['stop_id'] == i]['trip_id']
    for j in range(len(t_id)):
        stop_trip_map[i].append(t_id.values[j])
        
with open('processed_data.pkl', 'wb') as f:
    pickle.dump((stops_df, routes_df, shapes_df, trips_df, stops_list_df, dict_routes, lines_color_map, routes_trip_map, trip_stop_map, trip_stop_map_translated, list_list_stops, stop_time_map, stop_trip_map), f)