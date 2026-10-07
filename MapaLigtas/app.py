import json
import math
import os
import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="MapaLigtas")

# name, latitude, longitude, risk (1=Low, 2=Moderate, 3=High, 4=Very High)
# All 30 cities and municipalities of Laguna.
# Coordinates are approximate town centers. Risk levels are TEAM ESTIMATES (lakeshore and
# low-lying towns rated higher, upland and foothill towns lower), reviewed periodically
# against DA-AMIA (Laguna CRVA Hazard Index), PAGASA and UP NOAH. Edit the numbers below
# whenever you update the data; the notice shown in the app does not need to change.
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
    # ---- Added to cover all 30 cities/municipalities of Laguna ----
    # Coordinates are approximate town centers. Risk levels below are ESTIMATES by the team:
    # lakeshore / low-lying towns rated higher, upland and foothill towns rated lower.
    # CHECK each one against the DA-AMIA Laguna hazard map, PAGASA, and UP NOAH before relying on it.
    ("Alaminos", 14.0636, 121.2461, 1),
    ("Cavinti", 14.2453, 121.5069, 1),
    ("Famy", 14.4389, 121.4469, 1),
    ("Kalayaan", 14.3253, 121.4814, 3),
    ("Luisiana", 14.1850, 121.5100, 1),
    ("Lumban", 14.2986, 121.4614, 3),
    ("Mabitac", 14.4306, 121.4264, 2),
    ("Magdalena", 14.2000, 121.4333, 1),
    ("Majayjay", 14.1469, 121.4753, 1),
    ("Paete", 14.3636, 121.4836, 2),
    ("Pakil", 14.3797, 121.4778, 2),
    ("Pangil", 14.4025, 121.4594, 2),
    ("Pila", 14.2333, 121.3667, 3),
    ("Rizal", 14.1100, 121.3989, 1),
    ("San Pablo", 14.0683, 121.3256, 1),
    ("Santa Maria", 14.4608, 121.4261, 3),
    ("Victoria", 14.2250, 121.3256, 3),
]
areas.sort(key=lambda a: a[0])  # alphabetical, easier to scan in the dropdowns

colors = {1: "green", 2: "gold", 3: "orange", 4: "red"}
icons = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴"}

# Each item has (English, Filipino)
names = {1: ("Low", "Mababa"), 2: ("Moderate", "Katamtaman"),
         3: ("High", "Mataas"), 4: ("Very High", "Napakataas")}
tips = {
    1: ("Generally safer. Stay alert during heavy rain.",
        "Mas ligtas sa pangkalahatan. Manatiling alerto kapag malakas ang ulan."),
    2: ("Some flooding is possible. Check PAGASA updates.",
        "Maaaring bahain. Tingnan ang updates ng PAGASA."),
    3: ("Likely to flood. Avoid low roads and prepare to move.",
        "Malamang bahain. Iwasan ang mabababang daan at maghanda."),
    4: ("Very likely to flood. Avoid this area and follow your LGU's advice.",
        "Napakalamang bahain. Iwasan ang lugar na ito at sundin ang payo ng LGU."),
}

text = {
    "English": {
        "sample": "Prototype: risk levels are estimates maintained by the project team and updated periodically. Always check official PAGASA and UP NOAH updates.",
        "legend": "Risk levels",
        "pick": "Choose a place in Laguna",
        "risk": "Risk",
        "links": "Official information",
        "find": "Find places near me",
        "hint": "Click the button below, then choose Allow when your browser asks for your location.",
        "radius": "Show places within (km)",
        "fake": "Or test as if you were in:",
        "you": "You are here",
        "away": "km away",
        "warn": "Warning: {n} High or Very High risk area(s) within {r} km of you.",
        "safe": "No High or Very High risk areas within {r} km of you. Stay alert during heavy rain.",
        "none": "No mapped areas within {r} km. Try a larger distance.",
        "outside": "You appear to be outside Laguna. MapaLigtas only covers Laguna.",
        "privacy": "Privacy: your location is used only to find nearby areas. This app does not save it (Data Privacy Act of 2012, RA 10173).",
    },
    "Filipino": {
        "sample": "Prototype: ang mga antas ng panganib ay pagtatantya ng project team at regular na ina-update. Laging tingnan ang opisyal na updates ng PAGASA at UP NOAH.",
        "legend": "Antas ng panganib",
        "pick": "Pumili ng lugar sa Laguna",
        "risk": "Panganib",
        "links": "Opisyal na impormasyon",
        "find": "Hanapin ang mga lugar na malapit sa akin",
        "hint": "Pindutin ang button sa ibaba, at piliin ang Allow kapag hiningi ng browser ang iyong lokasyon.",
        "radius": "Ipakita ang mga lugar sa loob ng (km)",
        "fake": "O subukan na para bang nasa:",
        "you": "Ikaw ay nandito",
        "away": "km ang layo",
        "warn": "Babala: {n} lugar na Mataas o Napakataas ang panganib sa loob ng {r} km mula sa iyo.",
        "safe": "Walang lugar na Mataas o Napakataas ang panganib sa loob ng {r} km. Manatiling alerto kapag malakas ang ulan.",
        "none": "Walang mapang lugar sa loob ng {r} km. Subukan ang mas malaking distansya.",
        "outside": "Mukhang nasa labas ka ng Laguna. Laguna lamang ang sakop ng MapaLigtas.",
        "privacy": "Privacy: ginagamit lamang ang iyong lokasyon para hanapin ang mga kalapit na lugar. Hindi ito sine-save ng app na ito (Data Privacy Act of 2012, RA 10173).",
    },
}


def distance_km(lat1, lng1, lat2, lng2):
    """Distance between two points on Earth, in kilometers."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlng = math.radians(lng2 - lng1)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


# ---------- The page ----------
language = st.radio("Language / Wika", ["English", "Filipino"], horizontal=True)
i = 0 if language == "English" else 1   # 0 = English, 1 = Filipino
t = text[language]

st.title("MapaLigtas")
st.warning(t["sample"])

# ---------- Find places near me ----------
st.subheader(t["find"])
st.write(t["hint"])
loc = streamlit_geolocation()
if loc and loc.get("latitude") is not None:
    st.session_state["pos"] = (loc["latitude"], loc["longitude"])

radius = st.slider(t["radius"], 1, 20, 5)

fake = st.selectbox(t["fake"], ["-"] + [a[0] for a in areas])
pos = st.session_state.get("pos")
if fake != "-":
    for name, lat, lng, risk in areas:
        if name == fake:
            pos = (lat, lng)

in_laguna = False
if pos:
    in_laguna = 13.9 < pos[0] < 14.65 and 120.9 < pos[1] < 121.7
    if not in_laguna:
        st.warning(t["outside"])
    else:
        nearby = []
        for name, lat, lng, risk in areas:
            d = distance_km(pos[0], pos[1], lat, lng)
            if d <= radius:
                nearby.append((d, name, risk))
        nearby.sort()
        high = [n for n in nearby if n[2] >= 3]

        if not nearby:
            st.info(t["none"].format(r=radius))
        elif high:
            st.error(t["warn"].format(n=len(high), r=radius))
        else:
            st.success(t["safe"].format(r=radius))

        for d, name, risk in nearby:
            st.write(f"{icons[risk]} **{name}** – {names[risk][i]} – {d:.1f} {t['away']}")

# ---------- Map ----------
# Rough bounding box of Laguna province: [south-west], [north-east]
LAGUNA_BOUNDS = [[13.92, 120.99], [14.62, 121.68]]

center = list(pos) if in_laguna else [14.27, 121.25]
zoom = 11 if in_laguna else 10

my_map = folium.Map(
    location=center,
    zoom_start=zoom,
    min_zoom=10,                  # can't zoom out past Laguna
    max_bounds=True,              # can't drag away from Laguna
    min_lat=LAGUNA_BOUNDS[0][0], max_lat=LAGUNA_BOUNDS[1][0],
    min_lon=LAGUNA_BOUNDS[0][1], max_lon=LAGUNA_BOUNDS[1][1],
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
)
if not in_laguna:
    my_map.fit_bounds(LAGUNA_BOUNDS)

# Each town is drawn using its real boundary from laguna_municipalities.geojson
# (30 shapes, one per city/municipality, named exactly like the entries in `areas`).
# If the file is missing, the app falls back to the old circles so it never breaks.
BOUNDARY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "laguna_municipalities.geojson")
shapes = {}
if os.path.exists(BOUNDARY_FILE):
    with open(BOUNDARY_FILE, encoding="utf-8") as f:
        for feature in json.load(f)["features"]:
            shapes[feature["properties"]["name"]] = feature

for name, lat, lng, risk in areas:
    popup_text = f"<b>{name}</b><br>{t['risk']}: {names[risk][i]}<br>{tips[risk][i]}"
    tooltip_text = f"{name} – {names[risk][i]}"
    if name in shapes:
        folium.GeoJson(
            shapes[name],
            style_function=lambda f, c=colors[risk]: {
                "color": "#333333",      # thin border so neighboring towns are easy to tell apart
                "weight": 1.5,
                "fillColor": c,
                "fillOpacity": 0.25,
            },
            highlight_function=lambda f: {"weight": 3, "fillOpacity": 0.45},
            tooltip=tooltip_text,
            popup=folium.Popup(popup_text, max_width=250),
        ).add_to(my_map)
    else:
        folium.Circle(
            location=[lat, lng],
            radius=2500,
            color=colors[risk],
            fill=True,
            fill_opacity=0.4,
            popup=folium.Popup(popup_text, max_width=250),
        ).add_to(my_map)

if in_laguna:
    folium.Marker(list(pos), tooltip=t["you"]).add_to(my_map)

st_folium(my_map, height=450, width=700, returned_objects=[])

legend = "   ".join(f"{icons[r]} {names[r][i]}" for r in [1, 2, 3, 4])
st.write(f"**{t['legend']}:** {legend}")

# ---------- Pick a place ----------
choice = st.selectbox(t["pick"], [a[0] for a in areas])
for name, lat, lng, risk in areas:
    if name == choice:
        st.info(f"**{name}** – {t['risk']}: {names[risk][i]}. {tips[risk][i]}")

st.write(t["links"])
st.markdown("[PAGASA](https://www.pagasa.dost.gov.ph/flood) | [UP NOAH](https://noah.up.edu.ph/) | "
            "[DA-AMIA Laguna CRVA](https://amia.da.gov.ph/wp-content/uploads/2024/03/Laguna_CRVA_HazardIndex.pdf)")
st.caption(t["privacy"])
