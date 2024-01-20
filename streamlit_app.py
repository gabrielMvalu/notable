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

    # Textul care marchează sfârșitul datelor relevante
    stop_text = "Total active corporale"

    # Funcție pentru preluarea datelor începând cu rândul 4 până la textul stop
    def preluare_date(df):
        start_row = 3  # Începem cu rândul 4, indexarea este de la 0
        # Găsim rândul unde coloana 2 are valoarea stop_text
        end_row = df.index[df.iloc[:, 1] == stop_text].tolist()  
        # Dacă nu găsim valoarea, folosim toate rândurile
        end_row = end_row[0] if end_row else len(df)  
        # Selectăm rândurile dintre start_row și end_row
        date = df.iloc[start_row:end_row]
        return date

    # Butoane pentru generarea tabelelor
    if st.button("Generează Tabel 1"):
        if uploaded_file is not None:
            try:
                # Citim fișierul încărcat direct într-un DataFrame pandas
                df = pd.read_excel(uploaded_file, sheet_name="P. FINANCIAR")
                date = preluare_date(df)
                
                # Creăm tabelul cu datele relevante
                tabel_1 = date.copy()  # Sau alte operații de prelucrare dacă este necesar
                
                st.dataframe(tabel_1)  # Afișăm tabelul cu datele
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
