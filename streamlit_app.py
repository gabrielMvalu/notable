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

    
    def aranjeaza_coloana_2(df):
        # Identificăm rândurile pentru 'Total active corporale' și 'Total active necorporale'
        index_corporale_start = 3  # Presupunem că datele încep de la rândul 4
        index_corporale_end = df.index[df.iloc[:, 1].str.contains("Total active corporale", na=False)].tolist()[0]
        index_necorporale_end = df.index[df.iloc[:, 1].str.contains("Total active necorporale", na=False)].tolist()[0]
        
        # Extragem și păstrăm datele relevante
        df_corporale = df.iloc[index_corporale_start:index_corporale_end]
        df_necorporale = df.iloc[index_corporale_end + 1:index_necorporale_end]
    
        # Filtrăm valorile goale și nedorite
        df_corporale = df_corporale[df_corporale.iloc[:, 1].notna() & (df_corporale.iloc[:, 1] != 0) & (df_corporale.iloc[:, 1] != '-')]
        df_necorporale = df_necorporale[df_necorporale.iloc[:, 1].notna() & (df_necorporale.iloc[:, 1] != 0) & (df_necorporale.iloc[:, 1] != '-')]
    
        # Creăm lista cu valorile de eliminat
        valori_de_eliminat = [
            "Servicii de adaptare a utilajelor pentru operarea acestora de persoanele cu dizabilitati",
            "Rampa mobila", "Publicitate", "Consultanta management", 
            "Consultanta achizitii", "Consultanta scriere"
        ]
    
        # Eliminăm valorile nedorite din grupuri
        df_corporale = df_corporale[~df_corporale.iloc[:, 1].isin(valori_de_eliminat)]
        df_necorporale = df_necorporale[~df_necorporale.iloc[:, 1].isin(valori_de_eliminat)]
    
        # Creăm DataFrame-ul final cu coloana 2 aranjată
        tabel_final = pd.concat([df_corporale, df_necorporale]).reset_index(drop=True)
    
        # Adăugăm rândurile pentru subtotaluri și totaluri în locurile specificate
        # Vom adăuga valorile pentru aceste rânduri mai târziu, în prezent ne concentrăm pe structura coloanei
        tabel_final = tabel_final.append({"Denumire": "Total valoare cheltuieli cu investiția care contribuie substanțial la obiectivele de mediu"}, ignore_index=True)
        tabel_final = tabel_final.append({"Denumire": "Total valoare cheltuieli cu investiția care contribuie substanțial la egalitatea de șanse"}, ignore_index=True)
        tabel_final = tabel_final.append({"Denumire": "Valoare totala eligibila proiect"}, ignore_index=True)
    
        return tabel_final
    
    # Presupunem că 'df' este DataFrame-ul încărcat din foaia de calcul P. FINANCIAR
    # df = pd.read_excel('P_FINANCIAR.xlsx')  # Acesta este doar un exemplu, folosiți calea corectă a fișierului
    # tabel_final = aranjeaza_coloana_2(df)
    
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
