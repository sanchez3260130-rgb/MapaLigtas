import math
import os
import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="MapaLigtas")

# name, latitude, longitude, risk (1=Low, 2=Moderate, 3=High, 4=Very High)
# SAMPLE values. Replace with real UP NOAH / PAGASA / DA-AMIA data.
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
        "sample": "Prototype: risk levels are SAMPLE data. Always check official PAGASA and UP NOAH updates.",
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
        "sample": "Prototype: SAMPLE lamang ang mga antas ng panganib. Laging tingnan ang opisyal na updates ng PAGASA at UP NOAH.",
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
    in_laguna = 13.9 < pos[0] < 14.55 and 120.9 < pos[1] < 121.7
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
LAGUNA_BOUNDS = [[13.98, 121.00], [14.52, 121.65]]

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

# Optional: draw Laguna's exact outline if laguna.geojson is next to this file
if os.path.exists("laguna.geojson"):
    folium.GeoJson(
        "laguna.geojson",
        style_function=lambda f: {"color": "#1f4e79", "weight": 3, "fillOpacity": 0},
    ).add_to(my_map)

for name, lat, lng, risk in areas:
    popup_text = f"<b>{name}</b><br>{t['risk']}: {names[risk][i]}<br>{tips[risk][i]}"
    folium.Circle(
        location=[lat, lng],
        radius=3000,
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
st.markdown("[PAGASA](https://www.pagasa.dost.gov.ph/flood) | [UP NOAH](https://noah.up.edu.ph/)")
st.caption(t["privacy"])
