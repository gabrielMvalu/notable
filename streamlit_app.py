import streamlit as st
from PIL import Image
import pandas as pd
from io import BytesIO

def main():
    
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
        .title {
            color: #0078D4; /* A modern shade of blue */
            font-family: 'Roboto', sans-serif; /* Roboto is a modern and clean font */
            font-size: 30px; /* Adjust the size as needed */
            font-weight: 700; /* 700 is for bold text */
            text-align: center; /* Center align for modern aesthetics */
            margin-bottom: 20px; /* Add some space below the title */
        }
        </style>
    
        <h1 class='title'>Pregatirea datelor din P. FINANCIAR pentru completare tabel subcap 2.4</h1>
        """, unsafe_allow_html=True)


    
    # Sidebar pentru încărcarea și afișarea logo-ului și textului
    st.sidebar.title("Încărcarea Documentelor")
    logo_path = "LogoSTR.PNG"
    try:
        logo = Image.open(logo_path)
        st.sidebar.image(logo, use_column_width=True)
    except IOError:
        st.sidebar.error("Eroare la încărcarea logo-ului.")
    st.sidebar.markdown("<small>© Castemill S.R.L.</small>", unsafe_allow_html=True)
    # Încărcarea fișierului în sidebar
    uploaded_file = st.sidebar.file_uploader("Încarcă documentul '*.xlsx' aici", type="xlsx", accept_multiple_files=False)

    
    # Textul care marchează sfârșitul datelor relevante și începutul extracției
    stop_text = "Total proiect"
    # Funcție pentru preluarea și transformarea datelor
    def transforma_date(df):
        # Găsim rândul unde coloana 2 are valoarea stop_text
        stop_index = df.index[df.iloc[:, 1].eq(stop_text)].tolist()
        # Dacă găsim valoarea, folosim rândurile de la 4 până la acesta
        if stop_index:
            df = df.iloc[3:stop_index[0]]  # Ignorăm primele 3 rânduri și oprim la stop_text
        else:
            df = df.iloc[3:]  # Dacă stop_text nu este găsit, folosim totul de la rândul 4
        df = df[df.iloc[:, 1].notna() & (df.iloc[:, 1] != 0) & (df.iloc[:, 1] != '-')]        # Conversie la string pentru a evita erori la concatenare
        df.iloc[:, 6] = df.iloc[:, 6].astype(str)
        df.iloc[:, 7] = df.iloc[:, 7].astype(str)
        # Creăm un nou DataFrame cu coloanele specificate și datele mapate
        df_nou = pd.DataFrame({
            "Nr. crt.": df.iloc[:, 0],
            "Denumirea lucrărilor / bunurilor/ serviciilor": df.iloc[:, 1],
            "UM": "buc",
            "Cantitate": df.iloc[:, 11],
            "Preţ unitar (fără TVA)": df.iloc[:, 3],
            "Valoare Totală (fără TVA)": df.iloc[:, 2],
            "Linie bugetară": df.iloc[:, 14],
            "Eligibil/ neeligibil": "Eligibil: " + df.iloc[:, 6] + " // " + "Neeligibil: " + df.iloc[:, 7],
            "Contribuie la criteriile de evaluare a,b,c,d": "da"
        })
        return df_nou
        
    # Butoane pentru generarea tabelelor în sidebar
    if st.sidebar.button("Generează Tabel 1"):
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file, sheet_name="P. FINANCIAR")
                tabel_1 = transforma_date(df)
                st.dataframe(tabel_1)  # Afișăm tabelul transformat
                # Conversia DataFrame-ului într-un obiect Excel și crearea unui buton de descărcare
                towrite = BytesIO()
                tabel_1.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)  # Merem la începutul stream-ului
                st.download_button(label="Descarcă Tabelul 1 ca Excel",
                                   data=towrite,
                                   file_name="tabel_prelucrat.xlsx",
                                   mime="application/vnd.ms-excel")
            except ValueError as e:
                st.error(f"Eroare la procesarea datelor: {e}")
        else:
            st.error("Te rog să încarci un fișier.")

     

    def procesare_date_tabel2(df):
        # Identificăm rândurile specifice din P. FINANCIAR
        index_corporale = df.index[df.iloc[:, 1].str.contains("Total active corporale")].tolist()[0]
        index_necorporale = df.index[df.iloc[:, 1].str.contains("Total active necorporale")].tolist()[0]
        
        # Extragem rândurile dintre cele două totaluri și eliminăm valorile nedorite și rândurile goale
        df_filtrat = df.iloc[3:index_corporale]
        df_filtrat = df_filtrat[df_filtrat.iloc[:, 1].notna() & (df_filtrat.iloc[:, 1] != 0) & (df_filtrat.iloc[:, 1] != '-')]
        valori_de_eliminat = ["Servicii de adaptare a utilajelor pentru operarea acestora de persoanele cu dizabilitati",
                              "Rampa mobila", "Total active corporale", "Total active necorporale", 
                              "Publicitate", "Consultanta management", "Consultanta achizitii", "Consultanta scriere"]
        df_filtrat = df_filtrat[~df_filtrat.iloc[:, 1].isin(valori_de_eliminat)]
        
        # Calculăm subtotalul pentru cheltuielile ce contribuie la obiectivele de mediu
        subtotal_mediu = df_filtrat['Valoare Totală (fără TVA)'].sum()
    
        # Extragem și procesăm rândurile de după 'Total active corporale' până la 'Total active necorporale'
        df_egalitate = df.iloc[index_corporale + 1:index_necorporale]
        df_egalitate = df_egalitate[df_egalitate.iloc[:, 1].str.contains("Cursuri instruire personal|Toaleta ecologica")]
        df_egalitate = df_egalitate[df_egalitate.iloc[:, 1].notna() & (df_egalitate.iloc[:, 1] != 0) & (df_egalitate.iloc[:, 1] != '-')]
        
        # Calculăm subtotalul pentru cheltuielile ce contribuie la egalitatea de șanse
        subtotal_egalitate = df_egalitate['Valoare Totală (fără TVA)'].sum()
    
        # Calculăm totalul valorilor eligibile ale proiectului
        total_eligibil = subtotal_mediu + subtotal_egalitate
    
        # Creăm DataFrame-ul cu structura dorită
        tabel_final = pd.concat([
            df_filtrat, 
            pd.DataFrame([{'Denumire': 'Total valoare cheltuieli cu investiția care contribuie substanțial la obiectivele de mediu', 'Valoare Totală (fără TVA)': subtotal_mediu}]), 
            df_egalitate, 
            pd.DataFrame([{'Denumire': 'Total valoare cheltuieli cu investiția care contribuie substanțial la egalitatea de șanse', 'Valoare Totală (fără TVA)': subtotal_egalitate}]), 
            pd.DataFrame([{'Denumire': 'Valoare totala eligibila proiect', 'Valoare Totală (fără TVA)': total_eligibil}])
        ], ignore_index=True)
    
        return tabel_final
    
    # Presupunând că 'df' este DataFrame-ul încărcat din foaia de calcul P. FINANCIAR
    df = pd.read_excel('P_FINANCIAR.xlsx')  # Acesta este doar un exemplu, folosiți calea corectă a fișierului
    tabel_final = procesare_date_tabel2(df)
        
    
    # Butoane pentru generarea tabelelor în sidebar
    if st.sidebar.button("Generează Tabel 2"):
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file, sheet_name="P. FINANCIAR")
                # Generarea Tabelului 2
                tabel_2 = transforma_date_tabel2(df)
                # Afișăm tabelul transformat în aplicația Streamlit
                st.dataframe(tabel_2)
                # Conversia DataFrame-ului într-un obiect Excel și crearea unui buton de descărcare
                towrite = BytesIO()
                tabel_2.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)  # Ne reîntoarcem la începutul stream-ului pentru descărcare
                # Crearea butonului de descărcare pentru tabelul Excel
                st.download_button(label="Descarcă Tabelul 2 ca Excel",
                                   data=towrite,
                                   file_name="tabel_2_prelucrat.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.error(f"Eroare la procesarea datelor: {e}")
        else:
            st.error("Te rog să încarci un fișier.")
            
if __name__ == "__main__":
    main()
