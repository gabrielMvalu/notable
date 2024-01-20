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
    # Inițializăm un DataFrame gol pentru Tabelul 2
    tabel_2 = pd.DataFrame(columns=["Nr. crt.", "Denumire", "UM", "Cantitate", "Preţ unitar (fără TVA)", "Valoare Totală (fără TVA)"])
    
    # Variabila pentru a ține evidența numărului curent al criteriului
    numar_criteriu = 1
    
    # Extragerea utilajelor
    for index, row in df.iterrows():
        if row[1] == "Total active corporale":
            break
        tabel_2 = tabel_2.append({
            "Nr. crt.": numar_criteriu,
            "Denumire": row[1],
            "UM": "buc",
            "Cantitate": row[11],
            "Preţ unitar (fără TVA)": row[3],
            "Valoare Totală (fără TVA)": row[4]
        }, ignore_index=True)
        numar_criteriu += 1

    # Extragerea serviciilor
    # Presupunem că serviciile încep imediat după "Total active corporale"
    servicii_start_index = df.index[df.iloc[:, 1] == "Total active corporale"].tolist()[0] + 1
    servicii_end_index = df.index[df.iloc[:, 1] == "Total active necorporale"].tolist()[0]

    for index in range(servicii_start_index, servicii_end_index):
        tabel_2 = tabel_2.append({
            "Nr. crt.": numar_criteriu,
            "Denumire": df.iloc[index, 1],
            "UM": "buc",
            "Cantitate": df.iloc[index, 11],
            "Preţ unitar (fără TVA)": df.iloc[index, 3],
            "Valoare Totală (fără TVA)": df.iloc[index, 4]
        }, ignore_index=True)
        numar_criteriu += 1

    # Adăugarea totalurilor pentru active corporale și necorporale
    for total_text in ["Total active corporale", "Total active necorporale"]:
        total_index = df.index[df.iloc[:, 1] == total_text].tolist()[0]
        tabel_2 = tabel_2.append({
            "Nr. crt.": "",
            "Denumire": total_text,
            "UM": "",
            "Cantitate": "",
            "Preţ unitar (fără TVA)": "",
            "Valoare Totală (fără TVA)": df.iloc[total_index, 6]
        }, ignore_index=True)

    # Formatarea valorilor numerice cu două zecimale
    tabel_2["Cantitate"] = tabel_2["Cantitate"].apply(lambda x: '{:.2f}'.format(x) if pd.notnull(x) else x)
    tabel_2["Preţ unitar (fără TVA)"] = tabel_2["Preţ unitar (fără TVA)"].apply(lambda x: '{:.2f}'.format(x) if pd.notnull(x) else x)
    tabel_2["Valoare Totală (fără TVA)"] = tabel_2["Valoare Totală (fără TVA)"].apply(lambda x: '{:.2f}'.format(x) if pd.notnull(x) else x)

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
