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

    # Funcție pentru preluarea datelor de pe rândul 7
    def preluare_date_randul_7(df):
        if df.shape[0] >= 7:  # Verificăm dacă există cel puțin 7 rânduri
            date_randul_7 = df.iloc[6]  # Rândurile sunt indexate de la 0, așa că rândul 7 este la indexul 6
            return date_randul_7
        else:
            return None

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
                
                # Preluăm datele de pe rândul 7 și le adăugăm în tabelul 1
                date_randul_7 = preluare_date_randul_7(df)
                if date_randul_7 is not None:
                    # Aici vom adăuga logica de mapare a datelor din date_randul_7 în tabelul 1
                    # De exemplu, presupunând că coloana 2 din df este "Denumirea lucrărilor / bunurilor/ serviciilor":
                    tabel_1.loc[0] = [1, date_randul_7[1], 'buc', date_randul_7[3], date_randul_7[4], date_randul_7[5], '', '']
                    
                st.dataframe(tabel_1)  # Afișăm tabelul actualizat
            else:
                st.error("Foaia 'P. FINANCIAR' nu a fost găsită în document.")
        else:
            st.error("Te rog să încarci un fișier.")

    # Codul pentru butonul "Generează Tabel 2"
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
