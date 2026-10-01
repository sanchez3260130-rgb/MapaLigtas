import folium

# Each place: name, latitude, longitude, risk
# risk: 1 = Low, 2 = Moderate, 3 = High, 4 = Very High
areas = [
    ("San Pedro", 14.3595, 121.0473, 3),
    ("Biñan", 14.3333, 121.0806, 3),
    ("Santa Rosa", 14.3122, 121.1114, 2),
    ("Cabuyao", 14.2789, 121.1250, 3),
    ("Calamba", 14.2117, 121.1653, 3),
    ("Los Baños", 14.1699, 121.2436, 4),
    ("Bay", 14.1833, 121.2833, 4),
    ("Calauan", 14.1489, 121.3153, 2),
    ("Santa Cruz", 14.2814, 121.4161, 4),
    ("Pagsanjan", 14.2703, 121.4553, 3),
    ("Siniloan", 14.4169, 121.4470, 2),
    ("Nagcarlan", 14.1358, 121.4153, 1),
    ("Liliw", 14.1264, 121.4344, 1),
]
colors = {1: "green", 2: "yellow", 3: "orange", 4: "red"}
names = {1: "Low", 2: "Moderate", 3: "High", 4: "Very High"}

# Make a map locked to Laguna
LAGUNA_BOUNDS = [[13.98, 121.00], [14.52, 121.65]]

my_map = folium.Map(
    location=[14.27, 121.25],
    zoom_start=10,
    min_zoom=10,
    max_bounds=True,
    min_lat=13.98, max_lat=14.52,
    min_lon=121.00, max_lon=121.65,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
)
my_map.fit_bounds(LAGUNA_BOUNDS)

# Draw one colored circle for each place
for name, lat, lng, risk in areas:
    folium.Circle(
        location=[lat, lng],
        radius=3000,
        color=colors[risk],
        fill=True,
        popup=f"{name}: {names[risk]} risk",
    ).add_to(my_map)

my_map.save("map.html")
print("Done! Now double-click map.html")
