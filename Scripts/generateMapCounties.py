import folium
import json
import pandas as pd
from pathlib import Path

director_proiect = Path(__file__).resolve().parent
director_date = director_proiect / "Fisiere_deduplicate"
fisiere_csv = sorted(director_date)
if not fisiere_csv:
    raise FileNotFoundError(
        f"Nu am găsit fișiere CSV filtrate în '{director_date}'."
    )

# Încărcăm seturile filtrate și păstrăm sursa pentru fiecare eveniment.
seturi_date = []
for fisier_csv in fisiere_csv:
    date_fisier = pd.read_csv(fisier_csv)
    date_fisier["sursa"] = fisier_csv.name.replace(
        "_incendii_geolocalizat_meteo_Romania_fara_duplicate.csv", ""
    )
    seturi_date.append(date_fisier)

df = pd.concat(seturi_date, ignore_index=True, sort=False)
if "link" in df.columns:
    are_link = df["link"].notna() & df["link"].astype(str).str.strip().ne("")
    df_fara_link = df.loc[~are_link]
    df_cu_link = df.loc[are_link].drop_duplicates(
        subset=["link"], keep="first"
    )
    df = pd.concat([df_cu_link, df_fara_link], ignore_index=True)

# 2. Încărcăm fișierul GeoJSON
with (director_proiect / "romania_judete.geojson").open("r", encoding="utf-8") as f:
    geo_data = json.load(f)

# 3. Creăm harta centrată pe România
harta = folium.Map(
    location=[45.9432, 24.9668], 
    zoom_start=7,
)

# 4. Agregăm statisticile pe județe din CSV
# Standardizăm textul (eliminăm spațiile libere accidentale)
df['judet'] = df['judet'].astype(str).str.strip()
statistici_judete = df.loc[df['judet'].ne(""), 'judet'].value_counts().to_dict()

# 5. Adăugăm stratul de județe cu Folium GeoJson
# Folosim proprietatea 'name' extrasă din fișierul tău
folium.GeoJson(
    geo_data,
    name="Delimitare Județe",
    style_function=lambda feature: {
        # Dacă județul are incendii înregistrate în CSV, îl nuanțăm în portocaliu/roșu
        "fillColor": "#ff4d4d" if statistici_judete.get(feature["properties"]["name"], 0) > 0 else "#3388ff",
        "color": "#444444",
        "weight": 1.2,
        "fillOpacity": 0.35 if statistici_judete.get(feature["properties"]["name"], 0) > 0 else 0.06,
    },
    highlight_function=lambda feature: {
        "weight": 2.5,
        "color": "#000000",
        "fillOpacity": 0.5,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["name", "mnemonic", "region"],
        aliases=["Județ: ", "Indicativ: ", "Regiune: "],
        localize=True
    )
).add_to(harta)

# 6. Adăugăm markerele punctuale pentru fiecare incendiu
for _, row in df.iterrows():
    lat = row.get("latitudine")
    lon = row.get("longitudine")
    
    if pd.notna(lat) and pd.notna(lon):
        # Marker roșu pentru locație precisă, portocaliu pentru fallback pe sat/localitate
        culoare_marker = "red" if row.get("precizie_geocodare") == "precis" else "orange"
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; width: 230px;">
            <b style="color: #c0392b;">{row.get('titlu', 'Incendiu')}</b><br><hr style="margin: 4px 0;">
            <b>Localitate:</b> {row.get('localitate', '')} ({row.get('judet', '')})<br>
            <b>Dată incident:</b> {row.get('data', 'N/A')}<br>
            <b>Suprafață:</b> {row.get('suprafata_afectata', 'N/A')}<br>
            <b>Temp max:</b> {row.get('temp_max', 'N/A')} °C<br>
            <b>Vânt max:</b> {row.get('vant_max', 'N/A')} km/h<br><br>
            <b>Sursă:</b> {row.get('sursa', 'N/A')}<br>
            <a href="{row.get('link', '#')}" target="_blank">Deschide știrea sursă</a>
        </div>
        """
        
        folium.Marker(
            location=[float(lat), float(lon)],
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{row.get('localitate', 'Incident')} ({row.get('judet', '')})",
            icon=folium.Icon(color=culoare_marker, icon="fire", prefix="fa")
        ).add_to(harta)

# 7. Adăugăm controlul straturilor și salvăm rezultatul
folium.LayerControl().add_to(harta)
harta.save(str(director_proiect / "harta_romania_judete.html"))
print("Harta a fost generată cu succes în 'harta_romania_judete.html'!")