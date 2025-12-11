import streamlit as st
import func
from PIL import Image
import plotly.io as pio
pio.templates.default = None



#comentario meu
uploaded_file = st.file_uploader("Arraste seu arquivo FITS aqui", type=["fits"])
if uploaded_file is not None:
    if st.button("Gerar gráfico"):
        data=func.dados(uploaded_file)
        fig=func.figura(data[0],data[1],data[2])

        with open("figura.svg", "r", encoding="utf-8") as f:
            svg = f.read()

            st.markdown(svg, unsafe_allow_html=True)
        

