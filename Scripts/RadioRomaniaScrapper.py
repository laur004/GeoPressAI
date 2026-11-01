from playwright.sync_api import sync_playwright
import pandas as pd
import streamlit as st
import time


def scrape_article(link, file_name):
    with sync_playwright() as pw:

        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
    
        page = context.new_page()
        page.goto(link)

        # Accept cookies
        page.wait_for_selector("#onetrust-accept-btn-handler", timeout=10000)

        cookie_btn = page.locator("#onetrust-accept-btn-handler")
        if cookie_btn.count() > 0 and cookie_btn.is_visible():
            cookie_btn.click()
            print("Am acceptat cookie-urile.")

            page.wait_for_selector("#onetrust-consent-sdk", state="hidden")
            print("A disparut accept cookie page")


        page.wait_for_selector("div.widget-news.widget-news--B")
        rows = page.locator("div.widget-news.widget-news--B").all()
        extracted_data = []

        for row in rows[-3:]:
            articles = row.locator("div.news-item").all()
            for article in articles:

                thumbnail_loc = article.locator("div.thumb>img.wow.fadeIn")
                date_loc =  article.locator("span.news-item__date")
                title_loc = article.locator("div.news-item__title h2")
                desc_loc = article.locator("p.news-item__intro")
                link_loc = article.locator("a.link")

                extracted_data.append({
                    "data_publicare": date_loc.inner_text().strip() if date_loc.count() > 0 else "Fără dată",
                    "titlu": title_loc.inner_text().strip() if title_loc.count() > 0 else "Fără titlu",
                    "descriere": desc_loc.inner_text().strip() if desc_loc.count() > 0 else "Fără descriere",
                    "link": link_loc.get_attribute("href") if link_loc.count() > 0 else "Fără link",
                    "thumbnail": thumbnail_loc.get_attribute("src") if thumbnail_loc.count() > 0 else "Fără thumbnail"
                })

        for item in extracted_data:
            time.sleep(2)
            page.goto(item["link"])

            try:
                page.wait_for_selector("article.articol", timeout=5_000)

                strong_elements = page.locator("article.articol p:not(.articol__autor-data) strong").all_inner_texts()
                full_description = " ".join([text.strip() for text in strong_elements if text.strip()])
                
                paragraphs = page.locator("article.articol p").all_inner_texts()
                article_content = full_description + "\n" + "\n".join([p.strip() for p in paragraphs if p.strip()])
                item["full_description"] = full_description
                item["continut"] = article_content
                
            except Exception as e:
                print(f"Eroare la extragerea conținutului pentru {item['link']}: {e}")
                item["continut"] = "Eroare sau fără conținut"

        if extracted_data:
            df = pd.DataFrame(extracted_data)
            df.to_csv(file_name, index=False, encoding="utf-8")
            print(f"\nDatele au fost salvate cu succes în '{file_name}'!")
        else:
            print("\nNu am găsit date pentru a salva.")
        
        page.wait_for_event("close", timeout=0)
        print("Pagina a fost inchisa. Oprim scriptul...")
        browser.close()


def see_data(file_name):
    st.set_page_config(page_title="Articole Radio Constanța", layout="wide")
    st.title("🔥 Monitorizare Incendii de Vegetație")

    df = pd.read_csv(file_name)
    st.metric(label="Total articole extrase", value=len(df))

    # Afișare tabelară interactivă (poți sorta și căuta în ea)
    st.subheader("Baza de date generală")
    st.dataframe(df[["data_publicare", "titlu", "link"]], use_container_width=True)

    # Afișare detaliată pentru citirea conținutului
    st.subheader("Citește articolele")
    for index, row in df.iterrows():
        # Creăm o casetă extensibilă pentru fiecare articol
        with st.expander(f"{row['data_publicare']} | {row['titlu']}"):
            st.markdown(f"**Descriere:** {row['descriere']}")
            st.markdown(f"[🔗 Deschide pe site-ul original]({row['link']})")
            st.image(row["thumbnail"], use_container_width=True)
            st.divider()
            st.write(row['continut'])

def concat_data(main_file_name, extra_file_name):
    df1 = pd.read_csv(main_file_name)
    df2 = pd.read_csv(extra_file_name)
    df_concat = pd.concat([df1, df2], ignore_index=True)
    df_concat.to_csv(main_file_name, index=False, encoding="utf-8")



if __name__ == "__main__":
    MAIN_FILE_NAME = "RadioTimisoara_incendii.csv"
    EXTRA_FILE_NAME = "RadioTimisoara_incendii_pagina2.csv"

    #scrape_article("https://www.radiomures.ro/search/incendiu+vegetatie/page/2", MAIN_FILE_NAME)
    #see_data(MAIN_FILE_NAME)
    concat_data(MAIN_FILE_NAME, EXTRA_FILE_NAME)