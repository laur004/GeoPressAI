import pandas as pd
import requests
import time


def getMeteoData(row):
    lat = row['latitudine']
    long = row['longitudine']
    date = row['data']

    if pd.isna(lat) or pd.isna(long) or pd.isna(date):
        print(f" [Sărit] Coordonate sau dată lipsă: lat={lat}, lon={long}, data={date}")
        return None, None, None, None, None

    try:
        lat = float(str(lat).replace(',', '.'))
        long = float(str(long).replace(',', '.'))
    except ValueError:
        return None, None, None, None, None

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": long,
        "start_date": date,
        "end_date": date,
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,wind_speed_10m_max",
        "hourly": "relative_humidity_2m",
        "timezone": "auto"
    }

    try:
        time.sleep(2) # WAIT BETWEEN REQUESTS
        response = requests.get(url, params=params)

        if response.status_code !=200:
            print(f" [Eroare API] pentru {date}: {response.text}")
            return None, None, None, None, None

        meteo_data = response.json()

        temp_max = meteo_data['daily']['temperature_2m_max'][0]
        temp_min = meteo_data['daily']['temperature_2m_min'][0]
        temp_medie = meteo_data['daily']['temperature_2m_mean'][0]
        vant_max = meteo_data['daily']['wind_speed_10m_max'][0]
        
        umiditate_orara = [u for u in meteo_data['hourly']['relative_humidity_2m'] if u is not None]
        umiditate_medie = round(sum(umiditate_orara) / len(umiditate_orara), 2) if umiditate_orara else None
        
        print(f" [Succes] Extras meteo pentru: {meteo_data} ({row.get('localitate', '')}) | Temp max: {temp_max}°C")
        return temp_min, temp_max, temp_medie, umiditate_medie, vant_max
        
    except Exception as e:
        print(f" [Excepție] Cod Python crăpat la data {meteo_data}: {e}")
        return None, None, None, None, None


def meteo_enrichment(in_file_name, out_file_name):
    df = pd.read_csv(in_file_name)

    df.columns = df.columns.str.strip().str.replace('"', '')

    if not all(col in df.columns for col in ['latitudine', 'longitudine']):
        print(f"\n[EROARE CRITICĂ] Fișierul '{in_file_name}' NU conține coloanele 'latitudine' sau 'longitudine'!")
        return

    meteo_columns = ['temp_min', 'temp_max', 'temp_medie', 'umiditate_medie', 'vant_max']

    df[meteo_columns] = df.apply(getMeteoData, axis=1, result_type='expand')
    df.to_csv(out_file_name, encoding='utf-8')
    print(f"\nDatele au fost salvate în '{out_file_name}'!")



if __name__ == "__main__":

    IN_FILE_NAME = "RadioMures_incendii_geolocalizat.csv"
    OUT_FILE_NAME = "RadioMures_incendii_geolocalizat_meteo.csv"

    meteo_enrichment(IN_FILE_NAME, OUT_FILE_NAME)