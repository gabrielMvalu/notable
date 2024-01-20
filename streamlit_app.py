import streamlit as st
from PIL import Image
import pandas as pd

def main():
    st.title("Aplicația mea Streamlit")

    # Sidebar pentru încărcarea și afișarea logo-ului și textului
    st.sidebar.title("Încărcare Document")
    logo_path = "LogoSTR.PNG"
    try:
        logo = Image.open(logo_path)
        st.sidebar.image(logo, use_column_width=True)
    except IOError:
        st.sidebar.error("Eroare la încărcarea logo-ului.")
    st.sidebar.markdown("<small>© CASTEMILL SRL</small>", unsafe_allow_html=True)

    # Încărcarea fișierului
    uploaded_file = st.file_uploader("Încarcă documentul XLSX aici", type="xlsx", accept_multiple_files=False)

    # Funcție pentru verificarea existenței foii "P. FINANCIAR"
    def verifica_foaia_p_financiar(uploaded_file):
        try:
            # Citim fișierul încărcat direct într-un DataFrame pandas
            df = pd.read_excel(uploaded_file, sheet_name="P. FINANCIAR")
            return df, True
        except ValueError:
            # Dacă foaia nu există, întoarcem False
            return None, False

    # Butoane pentru generarea tabelelor
    if st.button("Generează Tabel 1"):
        if uploaded_file is not None:
            df, foaie_gasita = verifica_foaia_p_financiar(uploaded_file)
            if foaie_gasita:
                # Creăm un DataFrame gol cu header-ul pentru Tabelul 1
                header_tabel_1 = [
                    "Nr. crt.", "Denumirea lucrărilor / bunurilor/ serviciilor", "UM", 
                    "Cantitate", "Preţ unitar (fără TVA)", "Valoare Totală (fără TVA)",
                    "Linie bugetară Eligibil/ neeligibil", "Contribuie la criteriile de evaluare a,b,c,d"
                ]
                tabel_1 = pd.DataFrame(columns=header_tabel_1)
                st.dataframe(tabel_1)  # Afișăm tabelul gol
            else:
                st.error("Foaia 'P. FINANCIAR' nu a fost găsită în document.")

    if st.button("Generează Tabel 2"):
        if uploaded_file is not None:
            df, foaie_gasita = verifica_foaia_p_financiar(uploaded_file)
            if foaie_gasita:
                # Creăm un DataFrame gol cu header-ul pentru Tabelul 2
                header_tabel_2 = [
                    "Nr. crt.", "Denumirea lucrărilor / bunurilor/ serviciilor care contribuie substanțial la obiectivele de mediu și egalitatea de șanse, de tratament și accesibilitatea pentru persoanele cu dizabilități – conform sub-criteriilor D1 și D2 din cadrul criteriului de evaluare tehnica D", 
                    "UM", "Cantitate", "Preţ unitar (fără TVA)", "Valoare Totală (fără TVA)"
                ]
                tabel_2 = pd.DataFrame(columns=header_tabel_2)
                st.dataframe(tabel_2)  # Afișăm tabelul gol
            else:
                st.error("Foaia 'P. FINANCIAR' nu a fost găsită în document.")

if __name__ == "__main__":
    main()
