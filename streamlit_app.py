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

    # Buton pentru inițierea prelucrării datelor
    if st.button("Începe prelucrarea datelor"):
        if uploaded_file is not None:
            # Aici vei adăuga logica pentru prelucrarea datelor
            st.write("Fișier încărcat: ", uploaded_file.name)
        else:
            st.error("Te rog să încarci un fișier mai întâi.")

if __name__ == "__main__":
    main()

