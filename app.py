"""
APLICAÇÃO DE CONTROLE DE ESTUDOS
--------------------------------
Aplicação web para registro e análise de tempo de estudo desenvolvida com:
- Streamlit (interface)
- Pandas (análise de dados)
- SQLite (armazenamento)
"""

# BIBLIOTECAS ================================================================
import streamlit as st  # Framework para criação de aplicações web
import pandas as pd  # Manipulação e análise de dados
from datetime import datetime, time  # Manipulação de datas e horas
from db import init_db, inserir_registro, buscar_dados  # Funções de banco de dados

# CONFIGURAÇÃO INICIAL ======================================================
# Inicializa o banco de dados (cria tabelas se não existirem)
init_db()

# Configurações da página Streamlit
st.set_page_config(
    page_title="Controle de Estudos",  # Título da página
    layout="wide"  # Layout expandido
)

# ESTILO VISUAL =============================================================
# Aplica tema escuro personalizado via CSS embutido
st.markdown(
    '''
    <head>
        <link rel="icon" type="image/png" sizes="32x32" href="favicon-96x96.png">
    </head>
    <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="favicon-96x96.png">
    <link rel="manifest" href="site.webmanifest">
    <style>
    /* Cor de fundo geral */
    body {
        background-color: #0e1117;
        color: white;
    }
    /* Cor de fundo do container principal */
    .stApp {
        background-color: #0e1117;
    }
    </style>
    ''',
    unsafe_allow_html=True  # Permite injeção de HTML
)

# MENU LATERAL ==============================================================
# Cria menu de navegação na sidebar (barra lateral)
menu = st.sidebar.selectbox(
    "Menu",  # Título do seletor
    ["Inserir", "Planilha", "Estatísticas"]  # Opções disponíveis
)

# SEÇÃO DE INSERÇÃO DE DADOS ================================================
if menu == "Inserir":
    st.title("Adicionar Estudo")  # Título da seção
    
    # Divide a tela em duas colunas para melhor organização
    col1, col2 = st.columns(2)

    # COLUNA 1 - Dados básicos do estudo
    with col1:
        # Checkbox para usar a data e hora atual
        usar_agora = st.checkbox("Usar Agora", value=False)

        # Define data e hora com base no checkbox
        if usar_agora:
            now = datetime.now()
            data = st.date_input("Data", now.date(), disabled=True)
            hora = st.time_input("Hora", now.time().replace(microsecond=0), disabled=True)
        else:
            data = st.date_input("Data", datetime.today())
            hora = st.time_input("Hora", time(0, 0))

        materia = st.text_input("Matéria")  # Campo de texto para matéria estudada
    
    # COLUNA 2 - Metadados do estudo
    with col2:
        tempo = st.time_input(
            "Tempo de Estudo (hh:mm:ss)", 
            time(0,30)  # Valor padrão: 30 minutos
        )
        tipo = st.text_input("Tipo de Estudo")  # Ex: Leitura, Exercícios, Videoaula
        semana = st.number_input("Semana", 1, 60)  # Seletor numérico (1-60)

    # BOTÃO DE AÇÃO - Salva os dados no banco
    if st.button("Salvar"):
        # Combina data e hora em um único objeto datetime
        data_hora = datetime.combine(data, hora).isoformat()
        
        # Chama função para inserir no banco de dados
        inserir_registro(
            data_hora,  # Data e hora combinadas
            materia,    # Matéria estudada
            str(tempo), # Tempo de estudo (convertido para string)
            tipo,      # Tipo de estudo
            semana     # Número da semana
        )
        # Feedback visual para o usuário
        st.success("Registro salvo com sucesso!")

# SEÇÃO DE VISUALIZAÇÃO DE DADOS ============================================
elif menu == "Planilha":
    st.title("Registros de Estudo")  # Título da seção
    
    # Busca dados no banco (retorna colunas e registros)
    colunas, dados = buscar_dados()
    
    # Verifica se existem dados para mostrar
    if dados:
        # Cria DataFrame pandas para exibição
        df = pd.DataFrame(dados, columns=colunas)
        
        # Exibe tabela com todos os registros
        st.dataframe(
            df,
            use_container_width=True  # Ajusta largura ao container
        )

        # Prepara arquivo CSV para download
        csv = df.to_csv(index=False).encode('utf-8')
        
        # Botão de download
        st.download_button(
            "📁 Exportar CSV",  # Texto com ícone
            csv,  # Dados do arquivo
            "registros_estudo.csv",  # Nome do arquivo
            "text/csv",  # Tipo MIME
            key='download-csv'  # Chave única
        )
    else:
        # Mensagem alternativa caso não haja dados
        st.info("Nenhum dado registrado ainda.")

# SEÇÃO DE ANÁLISE ESTATÍSTICA ==============================================
elif menu == "Estatísticas":
    st.title("Estatísticas 📊")  # Título com emoji
    
    # Busca dados no banco
    colunas, dados = buscar_dados()
    
    # Verifica se existem dados para análise
    if dados:
        # Cria DataFrame pandas
        df = pd.DataFrame(dados, columns=colunas)
        
        # TRANSFORMAÇÕES DOS DADOS:
        # Converte tempo de estudo para minutos (facilita análise)
        df["minutos"] = pd.to_timedelta(df["tempo"]).dt.total_seconds() / 60
        
        # Converte string para datetime
        df["data_hora"] = pd.to_datetime(df["data_hora"])
        
        # Garante que semana seja numérico
        df["semana"] = df["semana"].astype(int)

        # LAYOUT DE GRÁFICOS (2 colunas)
        col1, col2 = st.columns(2)
        
        # GRÁFICO 1 - Tempo por matéria (barras)
        with col1:
            st.subheader("Tempo por Matéria")
            st.bar_chart(
                df.groupby("materia")["minutos"].sum()  # Agrupa e soma por matéria
            )

        # GRÁFICO 2 - Evolução semanal (linhas)
        with col2:
            st.subheader("Tempo por Semana")
            st.line_chart(
                df.groupby("semana")["minutos"].sum()  # Agrupa e soma por semana
            )
    else:
        # Mensagem alternativa caso não haja dados
        st.info("Nenhum dado para gerar estatísticas.")