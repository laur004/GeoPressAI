# GeoPressAI

### Echipa:
- [Andruță Andra-Mihaela](https://github.com/andra2602)
- [Ungureanu Matei](https://github.com/mateiungureanu)
- [Fugulin Victor](https://github.com/JubyJubson)
- [Sarighioleanu Sebastian-Laurențiu](https://github.com/laur004)


## Instalare dependinte folosind uv Package Manager
1) Deschide un terminal in folderul proiectului si ruleaza:
```bash
uv venv
```

```bash
.venv\Scripts\activate
```

Daca comanda anterioara nu a functionat incearca:

```bash
.\venv\Scripts\Activate.ps1
```

2) Instaleaza pachetele necesare:
```bash
uv pip install playwright parsel beautifulsoup4
playwright install chromium
uv pip install pandas
uv pip install streamlit
uv pip install python-dotenv
uv pip install openai
uv pip install folium
uv pip install geopy
```

## Colectarea datelor - Web Scrapper

### Date colectate:
1) link-ul
2) titlu
3) text
4) data
5) tip eveniment


### Fenomene de interes si metoda de cautare pe site-uri
1) incendii de vegetatie: in search bar caut "incendiu vegetatie"
2) inundatii/viituri: in search bar caut "inundatii"
3) alunecari de terene: in search bar caut "alunecari teren"


## Model AI pentru extragerea entitatilor - Qwen 3.5 - 9B GGUF

Modelul trebuie sa extraga:
- locatia producerii evenimentului(pentru localizare precisa vom folosi )
- momentul producerii/detectarii (data+ora)
- cauzele (daca sunt mentionate in articol)
- pagube / numarul de vieti omenesti pierdute

## Localizarea evenimentului - geocodare folosind Nominatim

Folosim acest API pentru a localiza cat mai precis evenimentul utilizand informatia furnizata de LLM la pasul anterior(locatia producerii evenimentului).

## Date meteorologice - Open Meteo

Folosim acest API pentru a extrage urmatoarele date de interes:
- temp_min
- temp_max
- temp_medie
- umiditate_medie
- vant_max

## Vizualizare harta Romaniei pe judete(Choropleth Map)
- Folium (foloseste Leaflet.js Maps Library, dar permite generarea hartii direct din codul Python)
- Leaflet.js pentru aplicatia web completa


