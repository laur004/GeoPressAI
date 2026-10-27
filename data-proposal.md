# Dataset cu știri românești
#### Echipa: Ungureanu Matei, Sarighioleanu Laurentiu, Fugulin Victor, Andruta Andra



### 1. De ce acest dataset? La ce e bun și cine l-ar folosi? Ce aduce în plus față de ce există deja? Dacă construiți un set nou, de ce nu ajunge unul existent?

Dezastrele naturale (incendiile de vegetație, inundațiile) sunt raportate în România în mare parte ca text liber în presă. Nu există o bază de date structurată, ușor de folosit, care să spună unde exact, când și ce tip de eveniment s-a produs, într-un format pe care îl poți pune pe hartă sau analiza statistic. Datele oficiale (ISU, ANM, ANAR) există, dar sunt împrăștiate, în formate diferite (rapoarte PDF, comunicate) și rar au locația precisă a evenimentului.

Datasetul nostru transformă știrile locale în înregistrări structurate: tip eveniment, localitate/județ/regiune, dată, plus datele meteo din ziua respectivă (temperatură, precipitații, vânt).

####  **Cine l-ar folosi:** 
- cercetători și studenți care analizează legătura dintre vreme și dezastre;
- instituții și ONG-uri de prevenție (identificarea zonelor și perioadelor cu risc);
- dezvoltatori de modele de NLP pentru română (extragere de locații și evenimente din text, clasificare de știri).

#### **Ce există deja și ce lipsește:**
- Bazele de date de evenimente (EM-DAT, EFFIS, Copernicus EMS) sunt structurate, dar pentru România listează evenimentele la nivel de județ, acoperă în principal evenimentele mari și nu conțin text ( https://data.jrc.ec.europa.eu/dataset/62f419a7-c264-5c90-b7c2-d1a358f3089f).
- Datele ISU despre intervenții există, într-o bază de peste 150.000 de intrări folosită într-un studiu academic, dar nu am găsit-o publicată ca set deschis (https://doi.org/10.24193/RCJ2023_10). 
- Corpusurile românești de text sunt generale: RONEC este un corpus pentru recunoașterea entităților denumite (https://github.com/dumitrescustefan/ronec), iar RoLargeSum are peste 615.000 de articole de presă, cu rezumate și cuvinte-cheie (https://github.com/avramandrei/rolargesum, https://arxiv.org/abs/2412.11317). Niciunul nu are etichete de tip eveniment, locație precisă sau date meteo. 
- Singurul set apropiat ca idee pe care l-am găsit extrage locația și impactul din articole despre dezastre, dar e construit pe presă indiană, în engleză (https://ieee-dataport.org/documents/dataset-extract-event-location-and-impact-information-disaster-news-articles). 

#### **De ce nu ajunge unul existent:**
 Din căutările noastre, nu am identificat un set în română care să combine știri locale, locație la nivel de localitate și date meteo. Seturile existente sunt la nivel de județ, acoperă mai ales evenimentele mari și nu au text sau legătură cu vremea. Evenimentele mici și locale apar doar în presa regională, iar tocmai acestea ne interesează. Datasetul nostru nu înlocuiește seturile existente, ci le completează: EFFIS și EM-DAT pot fi folosite pentru a valida evenimentele majore din setul nostru.

### 2. Surse. De unde luați datele: link, licență și dimensiune aproximativă. 

2.1 **Articolele de știri** vor fi colectate de pe site-urile Radio România (https://www.radioromania.ro/ ) pentru regiunile:

- Bacău
- Brașov
- București
- Cluj
- Constanța
- Oltenia Craiova
- Iași
- Reșița
- Târgu Mureș
- Timișoara

Vom filtra articolele din bara de căutare a site-ului folosind cuvinte cheie precum: “incendiu vegetatie”, “inundatie”.
Dimensiunea aproximativă: 500+ articole.

2.2  **Datele meteorologice** vor fi colectate folosind Open-Meteo API.
Licența: Gratuit pentru uz necomercial (licență tip CC BY 4.0).
Dimensiune: ~ numărul de articole.

### 3. Date sensibile. Conțin datele informații personale? Dacă da, ce faceți cu ele? Datele brute nu se urcă pe GitHub.
Datele sunt știri publice, deci riscul e mic, dar pot apărea informații personale în text:
- numele victimelor, ale persoanelor evacuate sau salvate;
- numele salvatorilor, pompierilor, primarilor sau altor oficiali;
- vârsta, ocupația sau adresa unei persoane (de exemplu „un bărbat de 67 de ani din satul X, strada Y”);
- numere de înmatriculare sau alte detalii care identifică o persoană;
- în cazuri rare, informații medicale despre victime (rănit, decedat, internat).

#### **Ce facem cu ele:**
- Detectăm numele de persoane cu un model NER pentru română (de exemplu un model BERT românesc fine-tunat pe NER).
- Înlocuim cu etichete generice: „Ion Popescu” devine „[PERSOANĂ]” sau „un individ”, iar o funcție rămâne generică („un pompier”, „primarul”).
- Generalizăm detaliile personale: adresa exactă devine localitatea, iar vârsta exactă devine un interval sau dispare.
- Păstrăm doar ce ne trebuie pentru scop: tipul evenimentului, locația la nivel de localitate/județ, data și numărul de victime (ca valoare numerică, fără identitate).
- Verificăm manual un eșantion (de exemplu 50 de articole) ca să măsurăm cât de bine a funcționat anonimizarea.

Datele brute (articolele originale) nu se urcă pe GitHub. Pe GitHub merge doar versiunea anonimizată, fără textul integral, cu link către sursă, ca să respectăm și drepturile de autor ale Radio România.

Locațiile (localități, județe) nu sunt date personale, deci le păstrăm, fiind esențiale pentru hartă.

### 4.  Schema. Cum arată o înregistrare în setul final: o schemă simplă (JSON, Pydantic sau tabel) și 2–3 exemple.

```json	
{
        "titlu": string,
        "data_publicarii": datetime,
        "link": string,
        "thumbnail": string,
        "descriere": string,
        "full_description": string,
        "continut": string,
        "entitati_extrase_ai": {
            "locatia": {
                "judet": string,
                "localitate": string,
                "locatie_specifica": string
            },
            "momentul_producerii": datetime,
            "suprafata_afectata": int,
            "cauzele": string
        },
        "geocodare": {
            "latitudine": float,
            "longitudine": float,
            "precizie_geocodare": string
        },
        "conditii_meteo": {
            "temp_min": float,
            "temp_max": float,
            "temp_medie": float,
            "umiditate_medie": float,
            "vant_max": float
        }
    }
```

Exemple de date pot fi găsite în același repository, în fișierul [`data/mostra_proiect.json`](data/mostra_proiect.json).

Un eșantion de 24 de înregistrări poate fi găsit tot în repository, în fișierul [`data/RadioConstanta_incendii.csv`](data/RadioConstanta_incendii.csv).

### 5. (Opțional) Cum veți arăta la final că setul vostru e util? O idee e suficientă.

Vom demonstra utilitatea datasetului printr-o aplicație web care afișează evenimentele pe harta României, distribuția lor pe regiuni și evoluția în timp, corelate cu datele meteo (Open-Meteo). 

Peste aceste date vom antrena un model simplu (de exemplu regresie logistică sau random forest) care estimează dacă parametrii meteo (temperatură, precipitații, vânt) influențează apariția evenimentelor, și vom identifica regiunile și perioadele cu risc crescut.
