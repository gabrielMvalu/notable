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

    # Textul care marchează sfârșitul datelor relevante și începutul extracției
    stop_text = "Total active corporale"

    # Funcție pentru preluarea și transformarea datelor
    def transforma_date(df):
        # Găsim rândul unde coloana 2 are valoarea stop_text
        stop_index = df.index[df.iloc[:, 1].eq(stop_text)].tolist()
        # Dacă găsim valoarea, folosim rândurile de la 4 până la acesta
        if stop_index:
            df = df.iloc[3:stop_index[0]]  # Ignorăm primele 3 rânduri și oprim la stop_text
        else:
            df = df.iloc[3:]  # Dacă stop_text nu este găsit, folosim totul de la rândul 4

        # Creăm un nou DataFrame cu coloanele specificate și datele mapate
        df_nou = pd.DataFrame({
            "Nr. crt.": df.iloc[:, 0],
            "Denumirea lucrărilor / bunurilor/ serviciilor": df.iloc[:, 1],
            "UM": "buc",
            "Cantitate": df.iloc[:, 11],
            "Preţ unitar (fără TVA)": df.iloc[:, 3],
            "Valoare Totală (fără TVA)": df.iloc[:, 2],
            "Linie bugetară": df.iloc[:, 14],
            "Eligibil/ neeligibil": df.iloc[:, 7] + " / " + df.iloc[:, 7],
            "Contribuie la criteriile de evaluare a,b,c,d": "da"
        })
        return df_nou

    # Butoane pentru generarea tabelelor
    if st.button("Generează Tabel 1"):
        if uploaded_file is not None:
            try:
                # Citim fișierul încărcat direct într-un DataFrame pandas
                df = pd.read_excel(uploaded_file, sheet_name="P. FINANCIAR")
                tabel_1 = transforma_date(df)
                st.dataframe(tabel_1)  # Afișăm tabelul transformat
            except ValueError as e:
                st.error(f"Eroare la procesarea datelor: {e}")
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
