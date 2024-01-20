import streamlit as st
from PIL import Image
import pandas as pd
from io import BytesIO

def main():
    st.title("Pregatirea datelor din P. FINANCIAR pentru completare tabel subcap 2.4")

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
        
        # Conversie la string pentru a evita erori la concatenare
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
            "Eligibil/ neeligibil": "Eligibil: " + df.iloc[:, 7] + " // " + "Neeligibil: " + df.iloc[:, 7],
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
                st.download_button(label="Descarcă Tabelul ca Excel",
                                   data=towrite,
                                   file_name="tabel_prelucrat.xlsx",
                                   mime="application/vnd.ms-excel")

            except ValueError as e:
                st.error(f"Eroare la procesarea datelor: {e}")
        else:
            st.error("Te rog să încarci un fișier.")

    def transforma_date_tabel2(df):
        # Găsim indexul pentru "Total active corporale" și "Total active necorporale"
        total_corporale_index = df.index[df.iloc[:, 1] == "Total active corporale"].tolist()
        total_necorporale_index = df.index[df.iloc[:, 1] == "Total active necorporale"].tolist()
    
        # Extragem utilajele și serviciile înainte de "Total active corporale"
        if total_corporale_index:
            utilaje_df = df.iloc[1:total_corporale_index[0]]  # Presupunem că header-ul este pe prima linie
        else:
            utilaje_df = df.iloc[1:]  # Dacă "Total active corporale" nu este găsit
    
        # Extragem serviciile între "Total active corporale" și "Total active necorporale"
        if total_corporale_index and total_necorporale_index:
            servicii_df = df.iloc[total_corporale_index[0] + 1:total_necorporale_index[0]]
        else:
            servicii_df = pd.DataFrame()  # Dacă nu sunt delimitări, nu avem servicii de extras
    
        # Unim utilajele și serviciile într-un singur DataFrame
        df_nou = pd.concat([utilaje_df, servicii_df], ignore_index=True)
    
        # Creăm noul DataFrame cu coloanele specificate
        tabel_2 = pd.DataFrame({
            "Nr. crt.": df_nou.iloc[:, 0],
            "Denumire": df_nou.iloc[:, 1],
            "UM": "buc",
            "Cantitate": df_nou.iloc[:, 11],
            "Preţ unitar (fără TVA)": df_nou.iloc[:, 3],
            "Valoare Totală (fără TVA)": df_nou.iloc[:, 4]
        })
    
        # Adăugăm rândurile pentru totaluri dacă există
        for total_text in ["Total active corporale", "Total active necorporale"]:
            total_index = df.index[df.iloc[:, 1] == total_text].tolist()
            if total_index:
                total_row = df.iloc[total_index[0], :]
                tabel_2 = tabel_2.append({
                    "Nr. crt.": "",
                    "Denumire": total_text,
                    "UM": "",
                    "Cantitate": "",
                    "Preţ unitar (fără TVA)": "",
                    "Valoare Totală (fără TVA)": total_row[6]
                }, ignore_index=True)
    
        return tabel_2
    # Butonul și logica pentru generarea Tabelului 2 și descărcarea acestuia
    if st.sidebar.button("Generează Tabel 2"):
        if uploaded_file is not None:
            try:
                # Citirea datelor din fișierul încărcat
                df = pd.read_excel(uploaded_file, sheet_name="P. FINANCIAR")
                
                # Generarea Tabelului 2
                tabel_2 = transforma_date_tabel2(df)
                
                # Afișarea Tabelului 2 în aplicația Streamlit
                st.dataframe(tabel_2)

                # Conversia tabelului într-un obiect Excel pentru a putea fi descărcat
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
