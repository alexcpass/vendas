import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard Comercial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS CUSTOMIZADO - VISUAL PROFISSIONAL
# ==========================================
st.markdown("""
    <style>
    /* Importar fonte Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Aplicar fonte em tudo */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fundo principal */
    .main {
        background-color: #f5f7fa;
    }
    
    /* Remover padding padrão */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    /* Sidebar escura */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f36 0%, #0f1419 100%);
        border-right: 1px solid #2d3748;
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label {
        color: #a0aec0 !important;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Cards de métricas */
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: #2c5282;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 13px;
        font-weight: 600;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stMetricDelta"] {
        font-size: 14px;
    }
    
    /* Títulos */
    h1 {
        color: #1a202c;
        font-weight: 700;
        font-size: 28px;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #2d3748;
        font-weight: 600;
        font-size: 20px;
        margin-top: 1.5rem;
    }
    
    h3 {
        color: #4a5568;
        font-weight: 600;
        font-size: 16px;
    }
    
    /* Botões personalizados */
    .stButton>button {
        background-color: #4299e1;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border: none;
        font-size: 14px;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #3182ce;
        box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
        transform: translateY(-1px);
    }
    
    /* Tabs estilo Metabase */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: white;
        padding: 8px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: transparent;
        border-radius: 6px;
        color: #4a5568;
        font-weight: 600;
        font-size: 14px;
        padding: 0 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4299e1 !important;
        color: white !important;
    }
    
    /* Containers brancos */
    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }
    
    /* File uploader */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #edf2f7;
        border: 2px dashed #cbd5e0;
        border-radius: 8px;
        padding: 2rem;
    }
    
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #4299e1;
        background-color: #e6f2ff;
    }
    
    /* Tabelas */
    .dataframe {
        font-size: 13px;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe thead tr th {
        background-color: #f7fafc !important;
        color: #2d3748 !important;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .dataframe tbody tr:hover {
        background-color: #f7fafc;
    }
    
    /* Remover menu hamburguer do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNÇÃO: PROCESSAR CSV UPLOADADO
# ==========================================
def process_uploaded_data(vendas_file, clientes_file, produtos_file):
    """Processa os arquivos CSV enviados pelo usuário"""
    try:
        # Ler CSVs
        vendas = pd.read_csv(vendas_file)
        clientes = pd.read_csv(clientes_file)
        produtos = pd.read_csv(produtos_file)
        
        # Merge modelo estrela
        df = vendas.merge(clientes, on='ClienteID', how='left')
        df = df.merge(produtos, on='ProdutoID', how='left')
        
        # Tratar ValorTotal (formato BR: 1.234,56)
        df['ValorTotal'] = (
            df['ValorTotal'].astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )
        
        # Tratar datas
        df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
        df['Ano'] = df['DataVenda'].dt.year
        df['Mes'] = df['DataVenda'].dt.month
        df['MesNome'] = df['Mes'].apply(
            lambda x: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][x-1]
        )
        
        return df, None
        
    except Exception as e:
        return None, str(e)

# ==========================================
# SIDEBAR: UPLOAD DE DADOS
# ==========================================
with st.sidebar:
    # Logo e título
    st.markdown("""
        <div style='text-align: center; padding: 20px 0 30px 0;'>
            <div style='font-size: 48px; margin-bottom: 10px;'>📊</div>
            <h2 style='color: white; margin: 0; font-size: 22px;'>Performance Comercial</h2>
            <p style='color: #a0aec0; font-size: 12px; margin-top: 5px;'>Dashboard de Vendas v2.0</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Seção de upload
    st.markdown("### 📤 CARREGAR DADOS")
    
    vendas_file = st.file_uploader(
        "Vendas",
        type=['csv'],
        key="vendas",
        help="Arquivo vendas.csv com transações"
    )
    
    clientes_file = st.file_uploader(
        "Clientes",
        type=['csv'],
        key="clientes",
        help="Arquivo clientes.csv com cadastro"
    )
    
    produtos_file = st.file_uploader(
        "Produtos",
        type=['csv'],
        key="produtos",
        help="Arquivo produtos.csv com catálogo"
    )
    
    arquivos_ok = all([vendas_file, clientes_file, produtos_file])
    
    if arquivos_ok:
        st.success("✅ 3/3 arquivos carregados")
    else:
        faltam = 3 - sum([bool(vendas_file), bool(clientes_file), bool(produtos_file)])
        st.warning(f"⚠️ Faltam {faltam} arquivo(s)")

# ==========================================
# PROCESSAR DADOS
# ==========================================
if not arquivos_ok:
    # Tela inicial quando não há dados
    st.markdown("""
        <div style='text-align: center; padding: 100px 20px;'>
            <div style='font-size: 72px; margin-bottom: 20px;'>📊</div>
            <h1 style='font-size: 36px; color: #2d3748; margin-bottom: 10px;'>Bem-vindo ao Dashboard Comercial</h1>
            <p style='font-size: 18px; color: #718096; margin-bottom: 40px;'>Carregue seus arquivos CSV na barra lateral para começar a análise</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Cards informativos
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <div style='font-size: 32px; margin-bottom: 15px;'>📤</div>
            <h3 style='color: #2d3748; margin-bottom: 10px;'>1. Upload Fácil</h3>
            <p style='color: #718096; font-size: 14px; line-height: 1.6;'>Arraste e solte seus arquivos CSV na barra lateral ou clique para selecionar</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info2:
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <div style='font-size: 32px; margin-bottom: 15px;'>⚡</div>
            <h3 style='color: #2d3748; margin-bottom: 10px;'>2. Processamento Automático</h3>
            <p style='color: #718096; font-size: 14px; line-height: 1.6;'>ETL completo em segundos: merge, limpeza e cálculo de métricas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info3:
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <div style='font-size: 32px; margin-bottom: 15px;'>📈</div>
            <h3 style='color: #2d3748; margin-bottom: 10px;'>3. Análise Interativa</h3>
            <p style='color: #718096; font-size: 14px; line-height: 1.6;'>Gráficos interativos, filtros dinâmicos e exportação de dados</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# Processar dados
with st.spinner('🔄 Processando dados...'):
    df, erro = process_uploaded_data(vendas_file, clientes_file, produtos_file)

if erro:
    st.error(f"❌ Erro ao processar arquivos: {erro}")
    st.stop()

# ==========================================
# HEADER DO DASHBOARD
# ==========================================
col_titulo, col_info = st.columns([3, 1])

with col_titulo:
    st.markdown(f"""
        <h1 style='margin-bottom: 5px;'>Performance Comercial</h1>
        <p style='color: #718096; font-size: 14px;'>Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
    """, unsafe_allow_html=True)

with col_info:
    st.markdown(f"""
        <div style='text-align: right; padding-top: 10px;'>
            <p style='color: #718096; font-size: 13px; margin: 0;'>Período</p>
            <p style='color: #2
