import pandas as pd
from geopy.geocoders import Nominatim
import time

geolocator = Nominatim(user_agent="GeoPressAI_Master", timeout=5)

def geolocate(row):
    jud = row['judet'] if pd.notna(row['judet']) else "",
    loc = row['localitate'] if pd.notna(row['localitate']) else ""
    spec = row['locatie_specifica'] if pd.notna(row['locatie_specifica']) else ""

    precise_address = f"{spec}, {loc}, {jud}, România".strip(", ")
    fallback_address = f"{loc}, {jud}, România".strip(", ")

    try:
        time.sleep(2) # WAIT BETWEEN REQUESTS
        if spec:
            location = geolocator.geocode(precise_address)
            if location:
                return location.latitude, location.longitude, "precis"

        location = geolocator.geocode(fallback_address)
        if location:
            return location.latitude, location.longitude, "sat"

    except Exception as e:
        print(f"Eroare la geocodare: {e}")
        time.sleep(2)

    return None, None, "eroare"

def geo_enrichment(in_file_name, out_file_name):
    df = pd.read_csv(in_file_name)

    lats = []
    longs = []
    precs = []

    for index, row in df.iterrows():
        lat, long, precision = geolocate(row)

        lats.append(lat)
        longs.append(long)
        precs.append(precision)

        print(f"Terminat de procesat randul {index}")

    df['latitudine'] = lats
    df['longitudine'] = longs
    df['precizie_geocodare'] = precs

    df.to_csv(out_file_name, index=False, encoding="utf-8")
    print(f"Datasetul a fost actualizat cu noile coordonate și salvat în: {out_file_name}")

def concat(main_file_name, extra_file_name):
    df1 = pd.read_csv(main_file_name)
    df2 = pd.read_csv(extra_file_name)
    df_concat = pd.concat([df1, df2], ignore_index=True)
    df_concat.to_csv(main_file_name, index=False, encoding="utf-8") 


if __name__ == "__main__":
    IN_FILE_NAME = "RadioMures_incendii_AI_enrichment.csv"
    OUT_FILE_NAME = "RadioMures_incendii_geolocalizat.csv"
    geo_enrichment(IN_FILE_NAME, OUT_FILE_NAME)

    #MAIN_FILE_NAME = "RadioConstanta_incendii_AI_enrichment.csv"
    #geo_enrichment(MAIN_FILE_NAME, OUT_FILE_NAME)
    #concat(MAIN_FILE_NAME, OUT_FILE_NAME)