import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Dashboard Comercial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main { background-color: #f5f7fa; }
    .block-container { padding-top: 2rem; }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f36 0%, #0f1419 100%);
    }
    section[data-testid="stSidebar"] * { color: white !important; }
    
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
    }
    
    h1 {
        color: #1a202c;
        font-weight: 700;
        font-size: 28px;
    }
    
    .stButton>button {
        background-color: #e2e8f0;
        color: #2d3748;
        border-radius: 6px;
        padding: 8px 20px;
        font-weight: 600;
        border: 1px solid #cbd5e0;
    }
    
    .stButton>button:hover {
        background-color: #cbd5e0;
        border-color: #4299e1;
    }
    
    .stButton>button[kind="primary"] {
        background-color: #4299e1 !important;
        color: white !important;
        border-color: #4299e1 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #e8ecf1;
        padding: 6px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: #4a5568;
        font-weight: 600;
        padding: 8px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #2d3748 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

def process_data(vendas_file, clientes_file, produtos_file, vendedores_file=None, regioes_file=None):
    try:
        vendas = pd.read_csv(vendas_file)
        clientes = pd.read_csv(clientes_file)
        produtos = pd.read_csv(produtos_file)
        
        df = vendas.merge(clientes, on='ClienteID', how='left')
        df = df.merge(produtos, on='ProdutoID', how='left')
        
        if vendedores_file is not None:
            vendedores = pd.read_csv(vendedores_file)
            df = df.merge(vendedores, on='VendedorID', how='left', suffixes=('', '_vendedor'))
            if 'Nome' in df.columns:
                df = df.rename(columns={'Nome': 'NomeVendedor'})
        
        df['ValorTotal'] = (
            df['ValorTotal'].astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )
        
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

# SIDEBAR
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px 0 30px 0;'>
            <div style='font-size: 48px;'>📊</div>
            <h2 style='margin: 10px 0 0 0; font-size: 20px;'>Performance Comercial</h2>
            <p style='color: #a0aec0; font-size: 11px; margin-top: 5px;'>Dashboard v2.0</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📤 CARREGAR DADOS")
    
    st.markdown("**Obrigatórios:**")
    vendas_file = st.file_uploader("Vendas.csv", type=['csv'], key="vendas")
    clientes_file = st.file_uploader("Clientes.csv", type=['csv'], key="clientes")
    produtos_file = st.file_uploader("Produtos.csv", type=['csv'], key="produtos")
    
    st.markdown("**Opcionais:**")
    vendedores_file = st.file_uploader("Vendedores.csv", type=['csv'], key="vendedores")
    regioes_file = st.file_uploader("Regiões.csv", type=['csv'], key="regioes")
    
    arquivos_obrigatorios = all([vendas_file, clientes_file, produtos_file])
    
    if arquivos_obrigatorios:
        total = 3 + sum([bool(vendedores_file), bool(regioes_file)])
        st.success(f"✅ {total}/5 arquivos carregados")
    else:
        faltam = 3 - sum([bool(vendas_file), bool(clientes_file), bool(produtos_file)])
        st.warning(f"⚠️ Faltam {faltam} arquivo(s)")

if not arquivos_obrigatorios:
    st.markdown("""
        <div style='text-align: center; padding: 80px 20px;'>
            <div style='font-size: 64px; margin-bottom: 20px;'>📊</div>
            <h1 style='font-size: 32px; margin-bottom: 10px;'>Bem-vindo ao Dashboard Comercial</h1>
            <p style='font-size: 16px; color: #718096;'>Carregue os arquivos CSV na barra lateral</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

with st.spinner('🔄 Processando dados...'):
    df, erro = process_data(vendas_file, clientes_file, produtos_file, vendedores_file, regioes_file)

if erro or df is None:
    st.error(f"❌ Erro: {erro}")
    st.stop()

# HEADER
st.markdown(f"""
    <div style='margin-bottom: 20px;'>
        <h1>Performance Comercial</h1>
        <p style='color: #718096; font-size: 14px;'>Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
    </div>
""", unsafe_allow_html=True)

# BOTÕES DE ANO (ESTILO METABASE)
st.markdown("<p style='font-size: 12px; color: #718096; font-weight: 600; margin-bottom: 10px;'>DASHBOARDS</p>", unsafe_allow_html=True)

anos_disponiveis = sorted(df['Ano'].unique().tolist())

if 'ano_selecionado' not in st.session_state:
    st.session_state.ano_selecionado = anos_disponiveis[-1]

cols_anos = st.columns([1.2] + [1]*(len(anos_disponiveis)) + [1, 1])

with cols_anos[0]:
    tipo = "primary" if st.session_state.ano_selecionado == "Todos" else "secondary"
    if st.button("Selecionar tudo", use_container_width=True, type=tipo, key="todos"):
        st.session_state.ano_selecionado = "Todos"
        st.rerun()

for idx, ano in enumerate(anos_disponiveis):
    with cols_anos[idx + 1]:
        tipo = "primary" if st.session_state.ano_selecionado == ano else "secondary"
        if st.button(str(ano), use_container_width=True, type=tipo, key=f"a{ano}"):
            st.session_state.ano_selecionado = ano
            st.rerun()

categorias_unicas = sorted(df['Categoria'].unique().tolist())
for idx, cat in enumerate(categorias_unicas):
    with cols_anos[len(anos_disponiveis) + 1 + idx]:
        if st.button(cat, use_container_width=True, key=f"c{cat}"):
            pass

st.markdown("---")

# FILTROS SIDEBAR
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 FILTROS AVANÇADOS")
    
    cat_sel = st.selectbox("Categoria", ['Todas'] + categorias_unicas)
    forma_sel = st.selectbox("Forma Pagamento", ['Todas'] + sorted(df['FormaPagamento'].unique().tolist()))
    
    st.markdown("---")
    st.markdown(f"""
        <div style='padding: 15px; background: rgba(66, 153, 225, 0.1); border-radius: 8px;'>
            <p style='font-size: 11px; color: #a0aec0; margin: 0;'>PERÍODO</p>
            <p style='font-size: 13px; margin: 5px 0 0 0;'>{df['DataVenda'].min().strftime('%d/%m/%Y')} a {df['DataVenda'].max().strftime('%d/%m/%Y')}</p>
        </div>
    """, unsafe_allow_html=True)

# APLICAR FILTROS
if st.session_state.ano_selecionado == "Todos":
    df_filtrado = df.copy()
else:
    df_filtrado = df[df['Ano'] == st.session_state.ano_selecionado].copy()

if cat_sel != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Categoria'] == cat_sel]

if forma_sel != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['FormaPagamento'] == forma_sel]

# KPIS
col1, col2, col3, col4 = st.columns(4)

faturamento = df_filtrado['ValorTotal'].sum()
vendas_qtd = df_filtrado['VendaID'].nunique()
ticket = faturamento / vendas_qtd if vendas_qtd > 0 else 0
produto_top = df_filtrado.groupby('NomeProduto')['ValorTotal'].sum().idxmax() if len(df_filtrado) > 0 else "N/A"

with col1:
    st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <p style='font-size: 12px; color: #718096; font-weight: 600; margin: 0; text-transform: uppercase;'>Total Vendas ($)</p>
            <p style='font-size: 28px; color: #2c5282; font-weight: 700; margin: 8px 0 0 0;'>R$ {faturamento:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <p style='font-size: 12px; color: #718096; font-weight: 600; margin: 0; text-transform: uppercase;'>Vendas (Qtd)</p>
            <p style='font-size: 28px; color: #16a34a; font-weight: 700; margin: 8px 0 0 0;'>{vendas_qtd:,}</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <p style='font-size: 12px; color: #718096; font-weight: 600; margin: 0; text-transform: uppercase;'>Ticket Médio</p>
            <p style='font-size: 28px; color: #9333ea; font-weight: 700; margin: 8px 0 0 0;'>R$ {ticket:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <p style='font-size: 12px; color: #718096; font-weight: 600; margin: 0; text-transform: uppercase;'>Produto Top</p>
            <p style='font-size: 18px; color: #ea580c; font-weight: 700; margin: 8
