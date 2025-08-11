import streamlit as st
import pandas as pd
import pycountry
import plotly.express as px

# --- Set page configuration ---
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide"
)

# --- Carregamento dos dados ---
#df = pd.read_csv('https://raw.githubusercontent.com/DaniloData/Dashboard-de-Salarios---Data-Science/refs/heads/main/dados_tratados.csv')
#df = pd.read_csv('https://raw.githubusercontent.com/DaniloData/Dashboard-de-Salarios---Data-Science/main/dados_tratados.csv')

df = pd.read_csv('dados_tratados.csv')

# --- Barra lateral (Filtros) ---
st.sidebar.header("🔍Filtros")

# Filtro do Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano:", anos_disponiveis, default=anos_disponiveis)

# Filtro senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade:", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por tipo de contrato
tipos_contrato_disponiveis = sorted(df['contrato'].unique())
tipos_contrato_selecionados = st.sidebar.multiselect("Tipo de Contrato:", tipos_contrato_disponiveis, default=tipos_contrato_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_empresa_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_empresa_selecionados = st.sidebar.multiselect("Tamanho da Empresa:", tamanhos_empresa_disponiveis, default=tamanhos_empresa_disponiveis)

# --- Filtagem do DAtaFrame ---
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(tipos_contrato_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_empresa_selecionados))
]

# --- Conteúdo principal ---

st.title("💰 Dashboard de Salários na Área de Dados")
st.subheader("Análise de Dados Salarial")
st.markdown("""Este dashboard permite explorar os salários na área de dados, filtrando por ano, senioridade, tipo de contrato e tamanho da empresa.
Utilize os filtros na barra lateral para personalizar a visualização dos dados.""")


# --- Métricas principais (KPIs) ---
st.subheader("📊 Métricas Principais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0].strip() 

else:
    salario_medio, saladio_mediano, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, 0, "N/A"

col1, col2, col3, col4 = st.columns(4)

col1.metric("Salário médio (USD)", f"${salario_medio:,.0f}")
col2.metric("Salário máximo (USD)", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Gráficos ---
st.subheader("📈 Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 Cargos por Salário Médio',
            labels={'usd': 'Salário Médio Anual (USD)', 'cargo': ''},
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis_title=('categoryorder : total ascending'))
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para o gráfico de Cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title='Distribuição de salário anuais',
            labels={'usd': 'Faixa salarial (USD)', 'count': ''},
        )
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para o gráfico de Distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5,
        )
        grafico_remoto.update_traces(textposition='inside', textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para o gráfico de Proporção dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
    # Calcular média salarial por país
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_do_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_pais = px.choropleth(media_do_pais,
    # MAPA
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            labels={'usd': 'Salário médio (USD)', "residencia_iso3": "País"},
            title='Salário médio de Data Scientists por País')
        grafico_pais.update_layout(title_x=0.1)
        st.plotly_chart(grafico_pais, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para o gráfico de Salário médio por País.")

# --- Tabela de dados detalhados ---
st.subheader("📋 Dados Detalhados")
st.dataframe(df_filtrado, use_container_width=True)

# --- Conclusão ---
st.subheader("📌 Conclusão")
st.markdown("""
Este dashboard oferece uma análise completa dos salários na área de dados, permitindo explorar tendências ao longo dos anos, níveis de senioridade, tipos de contrato e portes de empresa. Através de gráficos interativos e intuitivos, é possível identificar padrões relevantes e extrair insights valiosos, auxiliando profissionais e organizações na tomada de decisões estratégicas no setor de dados.
""")


