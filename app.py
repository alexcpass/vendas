import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard Financeiro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS CUSTOMIZADO
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: #1f77b4;
    }
    section[data-testid="stSidebar"] {
        background-color: #0a1929;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    h1 {
        color: #0a1929;
        font-weight: 700;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 10px;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNÇÃO DE PROCESSAMENTO DE DADOS
# ==========================================
def process_data(vendas_file, clientes_file, produtos_file):
    """
    Processa os arquivos carregados e retorna DataFrame tratado
    """
    # Ler arquivos
    vendas = pd.read_csv(vendas_file)
    clientes = pd.read_csv(clientes_file)
    produtos = pd.read_csv(produtos_file)
    
    # Merge
    df = vendas.merge(clientes, on='ClienteID', how='left')
    df = df.merge(produtos, on='ProdutoID', how='left')
    
    # Tratar ValorTotal
    df['ValorTotal'] = (
        df['ValorTotal']
        .astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )
    
    # Tratar datas
    df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
    df['Ano'] = df['DataVenda'].dt.year
    df['Mes'] = df['DataVenda'].dt.month
    df['MesNome'] = df['DataVenda'].dt.strftime('%b')
    
    return df

# ==========================================
# SIDEBAR - UPLOAD DE ARQUIVOS
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/combo-chart.png", width=80)
    st.title("📊 Dashboard Financeiro")
    st.markdown("---")
    
    st.subheader("📤 Carregar Dados")
    
    # Upload dos 3 arquivos
    vendas_upload = st.file_uploader(
        "Arquivo de Vendas",
        type=['csv'],
        help="Arquivo vendas.csv"
    )
    
    clientes_upload = st.file_uploader(
        "Arquivo de Clientes",
        type=['csv'],
        help="Arquivo clientes.csv"
    )
    
    produtos_upload = st.file_uploader(
        "Arquivo de Produtos",
        type=['csv'],
        help="Arquivo produtos.csv"
    )
    
    st.markdown("---")
    
    # Verificar se todos os arquivos foram carregados
    arquivos_carregados = all([vendas_upload, clientes_upload, produtos_upload])

# ==========================================
# VERIFICAR SE HÁ DADOS PARA PROCESSAR
# ==========================================
if not arquivos_carregados:
    # Página inicial quando não há dados
    st.title("👋 Bem-vindo ao Dashboard Financeiro")
    
    st.info("""
    ### 📤 Como começar:
    
    1. **Carregue os 3 arquivos CSV** na barra lateral:
       - vendas.csv
       - clientes.csv
       - produtos.csv
    
    2. O dashboard será gerado **automaticamente**
    
    3. Use os filtros para explorar os dados
    """)
    
    st.markdown("### 📋 Estrutura esperada dos arquivos:")
    
    col_ex1, col_ex2, col_ex3 = st.columns(3)
    
    with col_ex1:
        st.markdown("""
        **vendas.csv**
        - VendaID
        - DataVenda
        - ProdutoID
        - ClienteID
        - VendedorID
        - Quantidade
        - ValorTotal
        - FormaPagamento
        """)
    
    with col_ex2:
        st.markdown("""
        **clientes.csv**
        - ClienteID
        - NomeCliente
        - TipoCliente
        - Documento
        - Email
        - Telefone
        """)
    
    with col_ex3:
        st.markdown("""
        **produtos.csv**
        - ProdutoID
        - NomeProduto
        - Categoria
        - PrecoUnitario
        - EstoqueAtual
        """)
    
    st.stop()

# ==========================================
# PROCESSAR DADOS CARREGADOS
# ==========================================
try:
    with st.spinner('🔄 Processando dados...'):
        df = process_data(vendas_upload, clientes_upload, produtos_upload)
    
    st.success(f'✅ {len(df):,} registros carregados com sucesso!')
    
except Exception as e:
    st.error(f"""
    ❌ Erro ao processar arquivos: {str(e)}
    
    Verifique se os arquivos possuem as colunas corretas.
    """)
    st.stop()

# ==========================================
# FILTROS ADICIONAIS
# ==========================================
with st.sidebar:
    st.markdown("---")
    st.subheader("🔍 Filtros")
    
    anos = ['Todos'] + sorted(df['Ano'].unique().tolist())
    ano_selecionado = st.selectbox('📅 Ano', anos)
    
    categorias = ['Todas'] + sorted(df['Categoria'].unique().tolist())
    categoria_selecionada = st.selectbox('📦 Categoria', categorias)
    
    formas_pgto = ['Todas'] + sorted(df['FormaPagamento'].unique().tolist())
    forma_selecionada = st.selectbox('💳 Forma Pagamento', formas_pgto)

# Aplicar filtros
df_filtrado = df.copy()

if ano_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Ano'] == ano_selecionado]

if categoria_selecionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_selecionada]

if forma_selecionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['FormaPagamento'] == forma_selecionada]

# ==========================================
# HEADER
# ==========================================
st.title("📊 Dashboard Financeiro - Análise de Vendas")
periodo = f"Ano: {ano_selecionado}" if ano_selecionado != 'Todos' else "Período Completo"
st.markdown(f"**{periodo}** | Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("---")

# ==========================================
# KPIS
# ==========================================
col1, col2, col3, col4 = st.columns(4)

faturamento_total = df_filtrado['ValorTotal'].sum()
qtd_vendas = df_filtrado['VendaID'].nunique()
ticket_medio = faturamento_total / qtd_vendas if qtd_vendas > 0 else 0
clientes_unicos = df_filtrado['ClienteID'].nunique()

col1.metric("💰 Faturamento", f"R$ {faturamento_total:,.2f}")
col2.metric("🛒 Vendas", f"{qtd_vendas:,}")
col3.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}")
col4.metric("👥 Clientes", f"{clientes_unicos}")

st.markdown("---")

# ==========================================
# GRAFICOS COM PLOTLY (INTERATIVOS)
# ==========================================
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
    text='ValorTotal',
    title='Evolução Mensal',
    labels={'ValorTotal': 'Faturamento (R$)', 'MesNome': 'Mês'}
)

fig.update_traces(
    texttemplate='R$ %{text:,.0f}',
    textposition='outside',
    marker_color='#1f77b4'
)

fig.update_layout(height=400)

st.plotly_chart(fig, use_container_width=True)

# Duas colunas
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("🏆 Top 10 Produtos")
    
    top_produtos = (
        df_filtrado.groupby('NomeProduto')['ValorTotal']
        .sum()
        .reset_index()
        .sort_values('ValorTotal', ascending=False)
        .head(10)
    )
    
    fig_prod = px.bar(
        top_produtos,
        y='NomeProduto',
        x='ValorTotal',
        orientation='h',
        text='ValorTotal',
        color='ValorTotal',
        color_continuous_scale='Blues'
    )
    
    fig_prod.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
    fig_prod.update_layout(showlegend=False, height=400)
    
    st.plotly_chart(fig_prod, use_container_width=True)

with col_dir:
    st.subheader("💳 Formas de Pagamento")
    
    fat_pgto = (
        df_filtrado.groupby('FormaPagamento')['ValorTotal']
        .sum()
        .reset_index()
    )
    
    fig_pizza = px.pie(
        fat_pgto,
        values='ValorTotal',
        names='FormaPagamento',
        title='Distribuição por Pagamento',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
    fig_pizza.update_layout(height=400)
    
    st.plotly_chart(fig_pizza, use_container_width=True)

# ==========================================
# TABELA DE DETALHAMENTO
# ==========================================
st.markdown("---")
st.subheader("📋 Últimas 50 Vendas")

df_detalhes = df_filtrado[[
    'DataVenda', 'NomeCliente', 'NomeProduto', 
    'Quantidade', 'ValorTotal', 'FormaPagamento'
]].sort_values('DataVenda', ascending=False).head(50)

df_detalhes['DataVenda'] = df_detalhes['DataVenda'].dt.strftime('%d/%m/%Y')
df_detalhes['ValorTotal'] = df_detalhes['ValorTotal'].apply(lambda x: f'R$ {x:,.2f}')

st.dataframe(df_detalhes, use_container_width=True, height=400)

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption("Dashboard criado com Python + Streamlit | Dados carregados via upload")
