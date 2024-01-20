import streamlit as st
import os

# Funcție pentru încărcarea și afișarea logo-ului
def load_logo(logo_path):
    with open(logo_path, "rb") as file:
        st.image(file, width=100)  # Modifică width după necesități

def main():
    st.title("Aplicația mea Streamlit")

    # Încărcarea și afișarea logo-ului
    st.sidebar.title("Încărcare Document")
    logo_path = "LogoSTR.PNG"  # The logo is assumed to be in the same directory as the script
    logo = Image.open(logo_path)
    st.sidebar.image(logo, use_column_width=True)
  
    if os.path.exists(logo_path):
        load_logo(logo_path)
    else:
        st.write("Logo indisponibil")

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
