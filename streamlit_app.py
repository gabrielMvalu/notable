import streamlit as st
from PIL import Image
import pandas as pd
from io import BytesIO

def main():
    
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');
        .title {
            color: #7FBBE9; /* A modern shade of blue */
            font-family: 'Comic Sans MS', cursive, sans-serif; /* Comic Sans MS with fallbacks */
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
        stop_index = df.index[df.iloc[:, 1].eq(stop_text)].tolist()
        if stop_index:
            df = df.iloc[3:stop_index[0]]
        else:
            df = df.iloc[3:]
    
        df = df[df.iloc[:, 1].notna() & (df.iloc[:, 1] != 0) & (df.iloc[:, 1] != '-')]
    
        df.iloc[:, 6] = df.iloc[:, 6].astype(str)
        df.iloc[:, 7] = df.iloc[:, 7].astype(str)
    
        # Initialize an empty list for Nr. crt. and the columns that may be skipped
        nr_crt = []
        counter = 1
        um_list = []
        cantitate_list = []
        pret_unitar_list = []
        valoare_totala_list = []
        linie_bugetara_list = []
    
        for index, row in df.iterrows():
            item = row[1].strip().lower()
            # Check if the cell contains the specific text
            if item in ["total active corporale", "total active necorporale"]:
                nr_crt.append(None)  # Append None for these rows in Nr. crt.
                um_list.append(None)
                cantitate_list.append(None)
                pret_unitar_list.append(None)
                valoare_totala_list.append(None)
                linie_bugetara_list.append(None)
            else:
                nr_crt.append(counter)
                um_list.append("buc")
                cantitate_list.append(row[11])
                pret_unitar_list.append(row[3])
                valoare_totala_list.append(row[2])
                linie_bugetara_list.append(row[14])
                counter += 1  # Increment the counter only if the condition is not met
    
        df_nou = pd.DataFrame({
            "Nr. crt.": nr_crt,
            "Denumirea lucrărilor / bunurilor/ serviciilor": df.iloc[:, 1],
            "UM": um_list,
            "Cantitate": cantitate_list,
            "Preţ unitar (fără TVA)": pret_unitar_list,
            "Valoare Totală (fără TVA)": valoare_totala_list,
            "Linie bugetară": linie_bugetara_list,
            "Eligibil/ neeligibil": df.iloc[:, 6] + " // " + df.iloc[:, 7],
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
            
    def transforma_date_tabel2(df, stop_text):
        # Initial processing
        stop_index = df[df.iloc[:, 1] == stop_text].index.min()
        df_filtrat = df.iloc[3:stop_index] if pd.notna(stop_index) else df.iloc[3:]
        df_filtrat = df_filtrat[df_filtrat.iloc[:, 1].notna() & (df_filtrat.iloc[:, 1] != 0) & (df_filtrat.iloc[:, 1] != '-')]
    
        # Exclude specific values
        valori_de_eliminat = [
            "Servicii de adaptare a utilajelor pentru operarea acestora de persoanele cu dizabilitati",
            "Rampa mobila", "Total active corporale", "Total active necorporale", 
            "Publicitate", "Consultanta management", "Consultanta achizitii", "Consultanta scriere"
        ]
        df_filtrat = df_filtrat[~df_filtrat.iloc[:, 1].isin(valori_de_eliminat)]
    
        # Reordering for 'Cursuri instruire personal' and 'Toaleta ecologica'
        cursuri_index = df_filtrat.index[df_filtrat.iloc[:, 1] == "Cursuri instruire personal"].tolist()
        toaleta_index = df_filtrat.index[df_filtrat.iloc[:, 1] == "Toaleta ecologica"].tolist()
        if cursuri_index and toaleta_index:
            toaleta_row = df_filtrat.loc[toaleta_index[0]]
            df_filtrat = df_filtrat.drop(toaleta_index)
            upper_part = df_filtrat.iloc[:cursuri_index[0]]
            lower_part = df_filtrat.iloc[cursuri_index[0]:]
            df_filtrat = pd.concat([upper_part, toaleta_row.to_frame().T, lower_part])
    
        # Initialize lists for all columns
        nr_crt = []
        denumire = []
        um = []
        cantitate = []
        pret_unitar = []
        valoare_totala = []
    
        # Calculate subtotal values
        subtotal_1_sum = df_filtrat.iloc[:cursuri_index[0], 4].sum()  # Assuming 'Valoare Totală (fără TVA)' is the 5th column
        subtotal_2_sum = df_filtrat.iloc[cursuri_index[0]:toaleta_index[0]+1, 4].sum()
    
        # Process each item and handle special cases
        nr_crt_counter = 1
        for i, row in enumerate(df_filtrat.itertuples(), 1):
            item = row[2]  # Assuming 'Denumire' is the second column
    
            if item == "Cursuri instruire personal" or item == "Toaleta ecologica":
                if item == "Cursuri instruire personal":
                    nr_crt.append("Subtotal 1")
                    denumire.append("Total valoare cheltuieli cu investiția care contribuie substanțial la obiectivele de mediu")
                    valoare_totala.append(subtotal_1_sum)
                elif item == "Toaleta ecologica":
                    nr_crt.append(nr_crt_counter)
                    denumire.append(item)
                    valoare_totala.append(df_filtrat.iloc[i-1, 4])  # Assuming 'Valoare Totală (fără TVA)' is the 5th column
                    nr_crt_counter += 1
    
                    nr_crt.append("Subtotal 2")
                    denumire.append("Total valoare cheltuieli cu investiția care contribuie substanțial la egalitatea de șanse, de tratament și accesibilitatea pentru persoanele cu dizabilități")
                    valoare_totala.append(subtotal_2_sum)
                um.append(None)
                cantitate.append(None)
                pret_unitar.append(None)
            else:
                nr_crt.append(nr_crt_counter)
                denumire.append(item)
                um.append("buc")
                cantitate.append(df_filtrat.iloc[i-1, 11])  # Adjust the index as necessary
                pret_unitar.append(df_filtrat.iloc[i-1, 3])
                valoare_totala.append(df_filtrat.iloc[i-1, 4])
                nr_crt_counter += 1
    
        # Add final entries for 'Valoare totala eligibila proiect' and 'Pondere'
        valoare_totala_eligibila = df_filtrat.iloc[-1, 4]  # Assuming 'Valoare Totală (fără TVA)' is the 5th column
        nr_crt.extend([None, "Pondere", "Pondere"])
        denumire.extend([
            "Valoare totala eligibila proiect",
            "Total valoare cheltuieli cu investiția care contribuie substanțial la obiectivele de mediu / Valoare totala eligibila proiect",
            "Total valoare cheltuieli cu investiția care contribuie substanțial la egalitatea de șanse, de tratament și accesibilitatea pentru persoanele cu dizabilități / Valoare totala eligibila proiect"
        ])
        um.extend([None, None, None])
        cantitate.extend([None, None, None])
        pret_unitar.extend([None, None, None])
        valoare_totala.extend([
            valoare_totala_eligibila,
            subtotal_1_sum / valoare_totala_eligibila if valoare_totala_eligibila else 0,
            subtotal_2_sum / valoare_totala_eligibila if valoare_totala_eligibila else 0
        ])
    
        # Create the final DataFrame
        tabel_2 = pd.DataFrame({
            "Nr. crt.": nr_crt,
            "Denumire": denumire,
            "UM": um,
            "Cantitate": cantitate,
            "Preţ unitar (fără TVA)": pret_unitar,
            "Valoare Totală (fără TVA)": valoare_totala
        })
    
        return tabel_2



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
