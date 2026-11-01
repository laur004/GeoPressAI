import pandas as pd
from huggingface_hub import InferenceClient
import json
import time
from openai import OpenAI
import streamlit as st

client = OpenAI(base_url="http://localhost:1235/v1", api_key="lm-studio")

def extract_entities(text_articol, data_publicare):
    prompt = f"""
    Analizează următorul articol de știri din România despre un dezastru natural/incident.
    Returnează STRICT un obiect JSON valid, fără niciun alt text explicativ, respectând această structură:

    {{
        "locatia": {{
            "judet": "Numele județului (ex. Prahova). Dacă nu e menționat direct, dar se deduce din localitate, adaugă-l.",
            "localitate": "Numele orașului, comunei sau satului afectat.",
            "locatie_specifica": "Orice detaliu suplimentar exact: strada, cartierul, intersecția, versantul sau repere clare (ex. 'strada Principală', 'DJ 105 km 4'). Dacă nu există în text, returnează null."
        }},
        "momentul_producerii": {{
            "data": "Data producerii evenimentului în format YYYY-MM-DD. Dacă nu poate fi determinată, returnează null.",
            "ora": "Ora producerii evenimentului în format HH:MM, folosind formatul de 24 de ore. Dacă articolul menționează doar ora și minutele, completează secundele cu 00. Dacă ora nu poate fi determinată, returnează null.",
            "descriere_momentul_producerii": "Formularea din articol referitoare la momentul producerii evenimentului (ex. 'marți seara', 'în jurul orei 14:30'). Dacă nu există, returnează null."
        }},
        "suprafata_afectata": "Dimensiunea zonei afectate (ex. '50 hectare', '2000 mp'). Dacă nu e menționat, returnează null.",
        "pagube": "Victime umane, animale afectate, locuințe, utilaje sau alte bunuri materiale distruse. Dacă nu e menționat, returnează null.",
        "cauzele": "Motivul declanșării incidentului. Dacă nu e menționat, returnează null."
        
    }}

    Reguli pentru determinarea momentului producerii:

        - Nu confunda data publicării articolului cu data producerii evenimentului.
        - Folosește data publicării articolului ca reper pentru expresii relative precum 'astăzi', 'ieri' sau 'marți'.
        - Nu inventa o oră dacă aceasta nu este menționată sau nu poate fi dedusă în mod justificat.
        - Dacă data sau ora sunt aproximative, păstrează această informație în descriere_originala.
        - Toate datele și orele trebuie interpretate în fusul orar local al României. Nu adăuga un decalaj UTC dacă acesta nu poate fi stabilit corect.

    Regulă critică: Ignoră orașul de unde scrie jurnalistul sau unde este sediul autorităților și concentrează-te strict pe locul producerii evenimentului.

    Data publicarii: {data_publicare}
    Articol: {text_articol}
    """
    
    try:
        response = client.chat.completions.create(
                    model="qwen/qwen3.5-9b", # Numele nu contează; LM Studio folosește modelul deja încărcat
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                
        continut = response.choices[0].message.content
        
        # Curățăm potențialul format markdown adăugat de model
        if "```json" in continut:
            continut = continut.split("```json")[1].split("```")[0].strip()
            
        return json.loads(continut)
    except Exception as e:
        print(f"Eroare la extragere: {e}")





def add_entities_to_dataset(in_file_name, out_file_name):
    df = pd.read_csv(in_file_name)
    
    rezultate = []

    for index, row in df.iterrows():
        print(f"Procesez articolul {index}...")
        text_articol = str(row.get("description", row.get("continut", "")))
        data_publicare = row.get("data_publicare")

        date_extrase = extract_entities(text_articol, data_publicare)

        row_modificat = row.to_dict()
        loc = date_extrase.get("locatia") or {}

        row_modificat["judet"] = loc.get("judet")
        row_modificat["localitate"] = loc.get("localitate")
        row_modificat["locatie_specifica"] = loc.get("locatie_specifica")
        
        momentul_producerii = date_extrase.get("momentul_producerii") or {}
        
        row_modificat["data"] = momentul_producerii.get("data")
        row_modificat["ora"] = momentul_producerii.get("ora")
        row_modificat["descriere_momentul_producerii"] = momentul_producerii.get("descriere_momentul_producerii")

        row_modificat["suprafata_afectata"] = date_extrase.get("suprafata_afectata")
        row_modificat["pagube"] = date_extrase.get("pagube")
        row_modificat["cauzele"] = date_extrase.get("cauzele")
        
        rezultate.append(row_modificat)

    # Salvăm datele îmbogățite într-un nou fișier
    df_final = pd.DataFrame(rezultate)
    df_final.to_csv(out_file_name, index=False, encoding="utf-8")
    print(f"\nProcesare completă! Datele au fost salvate în '{out_file_name}'.")






def visualize_dataset_with_entities(file_name):
    
    st.set_page_config(page_title="Articole Radio Constanța", layout="wide")
    st.title("🔥 Monitorizare Incendii de Vegetație")

    df = pd.read_csv(file_name)
    st.metric(label="Total articole extrase", value=len(df))

    # Afișare tabelară interactivă (poți sorta și căuta în ea)
    st.subheader("Baza de date generală")
    st.dataframe(df[["data_publicare", "titlu", "link"]], width='stretch')

    # Afișare detaliată pentru citirea conținutului
    st.subheader("Citește articolele")
    for index, row in df.iterrows():
        # Creăm o casetă extensibilă pentru fiecare articol
        with st.expander(f"{row['data_publicare']} | {row['titlu']}"):
            st.markdown(f"**Descriere:** {row['descriere']}")
            st.markdown(f"[🔗 Deschide pe site-ul original]({row['link']})")
            st.image(row["thumbnail"], width='stretch')
            st.divider()
            st.write(row['continut'])

            st.divider()
            st.markdown(f"**Judet:** {row['judet']}")
            st.markdown(f"**Localitate:** {row['localitate']}")
            st.markdown(f"**Locatie specifica:** {row['locatie_specifica']}")

            st.markdown(f"**Data producerii:** {row['data']}")
            st.markdown(f"**Ora producerii:** {row['data']}")
            st.markdown(f"**Descriere momentul producerii:** {row['descriere_momentul_producerii']}")

            st.markdown(f"**Suprafata afectata:** {row['suprafata_afectata']}")
            st.markdown(f"**Pagube:** {row['pagube']}")
            st.markdown(f"**Cauzele:** {row['cauzele']}")
            
def concat_data(main_file_name, extra_file_name):
    df1 = pd.read_csv(main_file_name)
    df2 = pd.read_csv(extra_file_name)
    df_concat = pd.concat([df1, df2], ignore_index=True)
    df_concat.to_csv(main_file_name, index=False, encoding="utf-8")

if __name__ == "__main__":

    IN_FILE_NAME = "RadioTimisoara_incendii.csv"
    OUT_FILE_NAME = "RadioTimisoara_incendii_AI_enrichment.csv"

    #MAIN_FILE_NAME = "RadioConstanta_incendii_AI_enrichment.csv"

    add_entities_to_dataset(IN_FILE_NAME, OUT_FILE_NAME)
    #concat_data(MAIN_FILE_NAME, OUT_FILE_NAME)
    #visualize_dataset_with_entities(MAIN_FILE_NAME)