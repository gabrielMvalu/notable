import streamlit as st
from PIL import Image

def main():
    st.title("Aplicația mea Streamlit")

    # Sidebar pentru încărcarea și afișarea logo-ului
    st.sidebar.title("Rearanjare Tabel P. Financiar")
    logo_path = "LogoSTR.PNG"  # Presupunem că logo-ul este în același director cu scriptul
    try:
        logo = Image.open(logo_path)
        st.sidebar.image(logo, use_column_width=True)
    except IOError:
        st.sidebar.error("Eroare la încărcarea logo-ului.")

    # Adăugarea textului "© CASTEMILL SRL" în sidebar
    st.sidebar.markdown("<small>© Castemill S.R.L.</small>", unsafe_allow_html=True)
    
    # Încărcarea fișierului
    uploaded_file = st.file_uploader("Încarcă documentul XLSX aici", type="xlsx", accept_multiple_files=False)

   # Butoane pentru generarea tabelelor
    if st.button("Generează Tabel 1"):
        if uploaded_file is not None:
            # Logica pentru generarea Tabelului 1
            st.write("Generarea Tabelului 1 în curs...")
            # Aici va fi logica de prelucrare pentru Tabelul 1
        else:
            st.error("Te rog să încarci un fișier pentru a genera Tabelul 1.")

    if st.button("Generează Tabel 2"):
        if uploaded_file is not None:
            # Logica pentru generarea Tabelului 2
            st.write("Generarea Tabelului 2 în curs...")
            # Aici va fi logica de prelucrare pentru Tabelul 2
        else:
            st.error("Te rog să încarci un fișier pentru a genera Tabelul 2.")
if __name__ == "__main__":
    main()

