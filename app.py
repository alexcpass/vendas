import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector
from datetime import datetime

st.set_page_config(page_title="Dashboard Financeiro", page_icon="📊", layout="wide")

# ==========================================
# SIDEBAR: ESCOLHER FONTE DE DADOS
# ==========================================
with st.sidebar:
    st.title("📊 Dashboard Financeiro")
    st.markdown("---")
    
    st.subheader("🔌 Fonte de Dados")
    
    fonte = st.radio(
        "Escolha a origem:",
        ["📤 Upload de CSV", "🗄️ Conexão MySQL"],
        help="Upload: envie arquivos CSV | MySQL: conecte ao banco de dados"
    )
    
    st.markdown("---")

# ==========================================
# FUNÇÃO: PROCESSAR CSV
# ==========================================
def process_csv(vendas_file, clientes_file, produtos_file):
    vendas = pd.read_csv(vendas_file)
    clientes = pd.read_csv(clientes_file)
    produtos = pd.read_csv(produtos_file)
    
    df = vendas.merge(clientes, on='ClienteID', how='left')
    df = df.merge(produtos, on='ProdutoID', how='left')
    
    # Tratar ValorTotal
    df['ValorTotal'] = (
        df['ValorTotal'].astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )
    
    df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
    df['Ano'] = df['DataVenda'].dt.year
    df['Mes'] = df['DataVenda'].dt.month
    df['MesNome'] = df['DataVenda'].dt.strftime('%b')
    
    return df

# ==========================================
# FUNÇÃO: CARREGAR DO MYSQL
# ==========================================
@st.cache_data(ttl=600)
def load_from_mysql(host, user, password, database):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        vendas = pd.read_sql("SELECT * FROM vendas", conn)
        clientes = pd.read_sql("SELECT * FROM clientes", conn)
        produtos = pd.read_sql("SELECT * FROM produtos", conn)
        
        conn.close()
        
        df = vendas.merge(clientes, on='ClienteID', how='left')
        df = df.merge(produtos, on='ProdutoID', how='left')
        
        df['DataVenda'] = pd.to_datetime(df['DataVenda'])
        df['Ano'] = df['DataVenda'].dt.year
        df['Mes'] = df['DataVenda'].dt.month
        df['MesNome'] = df['DataVenda'].dt.strftime('%b')
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao conectar MySQL: {e}")
        return None

# ==========================================
# INTERFACE CONFORME FONTE ESCOLHIDA
# ==========================================
df = None

if fonte == "📤 Upload de CSV":
    with st.sidebar:
        st.subheader("📤 Carregar Arquivos")
        
        vendas_file = st.file_uploader("Vendas CSV", type=['csv'])
        clientes_file = st.file_uploader("Clientes CSV", type=['csv'])
        produtos_file = st.file_uploader("Produtos CSV", type=['csv'])
        
        if all([vendas_file, clientes_file, produtos_file]):
            with st.spinner('Processando...'):
                df = process_csv(vendas_file, clientes_file, produtos_file)
                st.success("✅ Dados carregados!")
        else:
            st.warning("⚠️ Carregue os 3 arquivos")

else:  # Conexão MySQL
    with st.sidebar:
        st.subheader("🗄️ Configurar MySQL")
        
        host = st.text_input("Host", value="localhost")
        user = st.text_input("Usuário", value="root")
        password = st.text_input("Senha", type="password")
        database = st.text_input("Database", value="vendas_db")
        
        if st.button("🔌 Conectar", use_container_width=True):
            with st.spinner('Conectando ao MySQL...'):
                df = load_from_mysql(host, user, password, database)
                
                if df is not None:
                    st.success(f"✅ Conectado! {len(df)} registros")

# ==========================================
# VERIFICAR SE HÁ DADOS
# ==========================================
if df is None or len(df) == 0:
    st.title("👋 Bem-vindo!")
    st.info("Configure a fonte de dados na barra lateral para começar.")
    st.stop()

# ==========================================
# FILTROS
# ==========================================
with st.sidebar:
    st.markdown("---")
    st.subheader("🔍 Filtros")
    
    anos = ['Todos'] + sorted(df['Ano'].unique().tolist())
    ano_selecionado = st.selectbox('Ano', anos)

df_filtrado = df[df['Ano'] == ano_selecionado] if ano_selecionado != 'Todos' else df

# ==========================================
# DASHBOARD (RESTO DO CÓDIGO...)
# ==========================================
st.title("📊 Dashboard Financeiro")
st.markdown(f"**Ano: {ano_selecionado}** | Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("---")

# KPIs
col1, col2, col3, col4 = st.columns(4)

faturamento = df_filtrado['ValorTotal'].sum()
vendas = df_filtrado['VendaID'].nunique()
ticket = faturamento / vendas if vendas > 0 else 0
clientes = df_filtrado['ClienteID'].nunique()

col1.metric("💰 Faturamento", f"R$ {faturamento:,.2f}")
col2.metric("🛒 Vendas", f"{vendas:,}")
col3.metric("🎯 Ticket Médio", f"R$ {ticket:,.2f}")
col4.metric("👥 Clientes", f"{clientes}")

# Gráfico mensal
st.subheader("📈 Faturamento Mensal")

fat_mensal = (
    df_filtrado.groupby(['Mes', 'MesNome'])['ValorTotal']
    .sum()
    .reset_index()
    .sort_values('Mes')
)

fig = px.bar(
    fat_mensal,
    x='MesNome',
    y='ValorTotal',
    text='ValorTotal'
)

fig.update_traces(
    texttemplate='R$ %{text:,.0f}',
    textposition='outside',
    marker_color='#1f77b4'
)

st.plotly_chart(fig, use_container_width=True)
