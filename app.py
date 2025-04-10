import streamlit as st
import pandas as pd
from datetime import datetime, time
from db import init_db, inserir_registro, buscar_dados

init_db()

st.set_page_config(page_title="Controle de Estudos", layout="wide")

# Tema escuro forçado
st.markdown(
    '''
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .stApp {
        background-color: #0e1117;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

menu = st.sidebar.selectbox("Menu", ["Inserir", "Planilha", "Estatísticas"])

if menu == "Inserir":
    st.title("Adicionar Estudo")
    col1, col2 = st.columns(2)

    with col1:
        data = st.date_input("Data", datetime.today())
        hora = st.time_input("Hora", time(0, 0))
        materia = st.text_input("Matéria")
    
    with col2:
        tempo = st.time_input("Tempo de Estudo (hh:mm:ss)", time(0,30))
        tipo = st.text_input("Tipo de Estudo")
        semana = st.number_input("Semana", 1, 60)

    if st.button("Salvar"):
        data_hora = datetime.combine(data, hora).isoformat()
        inserir_registro(data_hora, materia, str(tempo), tipo, semana)
        st.success("Registro salvo com sucesso!")

elif menu == "Planilha":
    st.title("Registros de Estudo")
    colunas, dados = buscar_dados()
    if dados:
        df = pd.DataFrame(dados, columns=colunas)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📁 Exportar CSV", csv, "registros_estudo.csv", "text/csv", key='download-csv')
    else:
        st.info("Nenhum dado registrado ainda.")

elif menu == "Estatísticas":
    st.title("Estatísticas 📊")
    colunas, dados = buscar_dados()
    if dados:
        df = pd.DataFrame(dados, columns=colunas)
        df["minutos"] = pd.to_timedelta(df["tempo"]).dt.total_seconds() / 60
        df["data_hora"] = pd.to_datetime(df["data_hora"])
        df["semana"] = df["semana"].astype(int)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Tempo por Matéria")
            st.bar_chart(df.groupby("materia")["minutos"].sum())

        with col2:
            st.subheader("Tempo por Semana")
            st.line_chart(df.groupby("semana")["minutos"].sum())
    else:
        st.info("Nenhum dado para gerar estatísticas.")
