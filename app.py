import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E CSS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Dashboard Comercial", page_icon="📊", layout="wide")

st.markdown("""
<style>
    /* Fundo Geral */
    .main { background-color: #f5f7fa; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1f36, #0f1419); }
    section[data-testid="stSidebar"] * { color: white !important; }
    
    /* Métricas (KPIs) */
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #2c5282; }
    
    /* BOTÕES DE ANO (Personalização Solicitada)
       - width: 100% para ocupar a coluna toda
       - padding reduzido para ficarem mais "baixos" */
    .stButton > button {
        width: 100%;
        padding-top: 5px;
        padding-bottom: 5px;
        font-weight: 600;
        border-radius: 6px;
    }
    .stButton>button[kind="primary"] { background-color: #4299e1; color: white; border: none; }
    .stButton>button[kind="secondary"] { background-color: #e2e8f0; color: #1a202c; border: none; }
    
    /* Ajuste de espaçamento do título */
    h1 { margin: 0; padding: 0; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. FUNÇÃO DE PROCESSAMENTO DE DADOS
# -----------------------------------------------------------------------------
@st.cache_data
def process_data(v, c, p):
    try:
        vendas = pd.read_csv(v)
        clientes = pd.read_csv(c)
        produtos = pd.read_csv(p)
        
        # Merge das tabelas
        df = vendas.merge(clientes, on='ClienteID', how='left').merge(produtos, on='ProdutoID', how='left')
        
        # Tratamento de Valor Monetário (padrão BR 1.000,00 -> python 1000.00)
        df['ValorTotal'] = (
            df['ValorTotal'].astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )
        
        # Tratamento de Datas
        df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
        df['Ano'] = df['DataVenda'].dt.year
        df['Mes'] = df['DataVenda'].dt.month
        
        # Nomes dos meses para ordenação correta
        meses_map = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
                     7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
        df['MesNome'] = df['Mes'].map(meses_map)
        
        return df
    except Exception as e:
        return None

# -----------------------------------------------------------------------------
# 3. SIDEBAR E UPLOAD
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<div style='text-align:center;padding:20px 0;'><div style='font-size:48px;'>📊</div><h2>Performance</h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📂 Upload de Dados")
    v_file = st.file_uploader("Vendas.csv", type=['csv'])
    c_file = st.file_uploader("Clientes.csv", type=['csv'])
    p_file = st.file_uploader("Produtos.csv", type=['csv'])

# Tela de bloqueio se não houver arquivos
if not all([v_file, c_file, p_file]):
    st.markdown("""
        <div style='text-align: center; padding: 80px;'>
            <h1 style='color: #cbd5e0;'>Aguardando Arquivos...</h1>
            <p style='color: #718096;'>Por favor, faça o upload de Vendas, Clientes e Produtos na barra lateral.</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# Processamento
df = process_data(v_file, c_file, p_file)

# -----------------------------------------------------------------------------
# 4. HEADER COM GRADIENTE (Azul Claro -> Verde Neon)
# -----------------------------------------------------------------------------
st.markdown("""
    <div style="
        background: linear-gradient(90deg, #dbeafe 0%, #d9f99d 100%); 
        padding: 20px 30px; 
        border-radius: 12px; 
        margin-bottom: 30px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h1 style="color: #1e3a8a; font-family: sans-serif; font-weight: 800; font-size: 32px;">Performance Comercial</h1>
        <p style="color: #475569; margin: 5px 0 0 0; font-size: 14px;">Visão Geral de Vendas e Estoque</p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. FILTRO DE ANO (BOTÕES LARGOS)
# -----------------------------------------------------------------------------
anos = sorted(df['Ano'].unique())
if 'ano' not in st.session_state: 
    st.session_state.ano = anos[-1]

st.markdown("### 📅 Período de Análise")
# Cria colunas: 1 para 'Todos' + 1 para cada ano + Espaço vazio no final
cols = st.columns([1] + [1]*len(anos) + [5])

with cols[0]:
    if st.button("Todos", type="primary" if st.session_state.ano == "Todos" else "secondary"):
        st.session_state.ano = "Todos"
        st.rerun()

for i, ano in enumerate(anos):
    with cols[i+1]:
        if st.button(str(ano), type="primary" if st.session_state.ano == ano else "secondary", key=f"btn_{ano}"):
            st.session_state.ano = ano
            st.rerun()

# -----------------------------------------------------------------------------
# 6. FILTROS LOGICOS E APLICAÇÃO
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 Filtros Detalhados")
    cat_opts = ['Todas'] + sorted(df['Categoria'].dropna().unique().tolist())
    cat_sel = st.selectbox("Categoria", cat_opts)
    
    pag_opts = ['Todas'] + sorted(df['FormaPagamento'].dropna().unique().tolist())
    pag_sel = st.selectbox("Forma de Pagamento", pag_opts)

# Aplicar filtros no DataFrame
df_filtered = df.copy()

if st.session_state.ano != "Todos":
    df_filtered = df_filtered[df_filtered['Ano'] == st.session_state.ano]

if cat_sel != 'Todas':
    df_filtered = df_filtered[df_filtered['Categoria'] == cat_sel]

if pag_sel != 'Todas':
    df_filtered = df_filtered[df_filtered['FormaPagamento'] == pag_sel]

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. KPIs (INDICADORES)
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

faturamento = df_filtered['ValorTotal'].sum()
qtd_vendas = df_filtered['VendaID'].nunique()
ticket_medio = faturamento / qtd_vendas if qtd_vendas > 0 else 0
clientes_unicos = df_filtered['ClienteID'].nunique()

col1.metric("💰 Faturamento Total", f"R$ {faturamento:,.0f}")
col2.metric("📦 Volume de Vendas", f"{qtd_vendas}")
col3.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.0f}")
col4.metric("👥 Clientes Ativos", f"{clientes_unicos}")

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. GRÁFICO 1: FATURAMENTO MENSAL (Barras)
# -----------------------------------------------------------------------------
st.markdown("### 📈 Evolução do Faturamento")

df_fat_mensal = df_filtered.groupby(['Mes', 'MesNome'])['ValorTotal'].sum().reset_index().sort_values('Mes')

fig_fat = px.bar(
    df_fat_mensal, 
    x='MesNome', 
    y='ValorTotal', 
    text='ValorTotal',
    color_discrete_sequence=['#4299e1']
)

fig_fat.update_traces(
    texttemplate='R$ %{text:,.0f}', 
    textposition='outside',
    name='Faturamento' # Nome para legenda
)

fig_fat.update_layout(
    height=350,
    plot_bgcolor='white',
    showlegend=True, # Legenda forçada
    margin=dict(t=30, b=0, l=0, r=0)
)

st.plotly_chart(fig_fat, use_container_width=True)

# -----------------------------------------------------------------------------
# 9. GRÁFICO 2: VOLUME DE VENDAS (MISTO: BARRAS + LINHAS + FUNDO AMARELO CLARO)
# -----------------------------------------------------------------------------
st.markdown("### 📊 Sazonalidade de Vendas")

df_vol_mensal = df_filtered.groupby(['Mes', 'MesNome'])['VendaID'].count().reset_index().sort_values('Mes')

fig_vol = go.Figure()

# Camada 1: Barras (Fundo suave)
fig_vol.add_trace(go.Bar(
    x=df_vol_mensal['MesNome'],
    y=df_vol_mensal['VendaID'],
    name='Volume (Barras)',
    marker_color='#b2dfdb',
    opacity=0.5,
    textposition='none' # Sem texto nas barras para não poluir
))

# Camada 2: Linha (Destaque)
fig_vol.add_trace(go.Scatter(
    x=df_vol_mensal['MesNome'], 
    y=df_vol_mensal['VendaID'],
    mode='lines+markers+text',
    name='Tendência (Linha)',
    line=dict(color='#2e7d32', width=4),
    marker=dict(size=10, color='#2e7d32', line=dict(color='white', width=2)),
    text=df_vol_mensal['VendaID'],
    textposition='top center',
    textfont=dict(size=14, color='black', weight='bold') # Texto PRETO
))

fig_vol.update_layout(
    height=400,
    plot_bgcolor='#FEFDE7',      # Fundo "Perolado/Amarelo Claro"
    paper_bgcolor='white',
    xaxis=dict(
        showgrid=False,
        tickfont=dict(color='black', size=12, weight='bold') # Meses em Preto
    ),
    yaxis=dict(
        showgrid=True, 
        gridcolor='#e0e0e0',
        title='Qtd. Vendas'
    ),
    showlegend=True,
    legend=dict(orientation="h", y=1.1, x=0),
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(fig_vol, use_container_width=True)

# -----------------------------------------------------------------------------
# 10. GRÁFICO 3: TOP 10 PRODUTOS (Horizontal, Ordenado, Rótulo Vermelho)
# -----------------------------------------------------------------------------
st.markdown("### 🏆 Top 10 Produtos (Maior Faturamento)")

df_top_prod = df_filtered.groupby('NomeProduto')['ValorTotal'].sum().reset_index()

# Ordenar do MENOR para o MAIOR (ascending=True) para que o Plotly
# desenhe o MAIOR no TOPO do gráfico horizontal.
df_top_prod = df_top_prod.sort_values('ValorTotal', ascending=True).tail(10)

fig_prod = px.bar(
    df_top_prod, 
    y='NomeProduto', 
    x='ValorTotal', 
    orientation='h', 
    text='ValorTotal',
    color='ValorTotal',
    color_continuous_scale='Blues'
)

fig_prod.update_traces(
    texttemplate='R$ %{text:,.0f}', 
    textposition='outside',
    textfont=dict(color='#d32f2f', weight='bold') # Rótulo VERMELHO
)

fig_prod.update_layout(
    height=450,
    plot_bgcolor='white',
    showlegend=False,
    xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
    coloraxis_showscale=False # Remove barra de cor lateral
)

st.plotly_chart(fig_prod, use_container_width=True)

# -----------------------------------------------------------------------------
# 11. TABELA DE DETALHAMENTO
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 📋 Registro de Vendas Recentes")

df_table = df_filtered[['DataVenda', 'NomeCliente', 'NomeProduto', 'Quantidade', 'ValorTotal', 'FormaPagamento']]
df_table = df_table.sort_values('DataVenda', ascending=False).head(50)

# Formatação visual para a tabela
df_table['DataVenda'] = df_table['DataVenda'].dt.strftime('%d/%m/%Y')
df_table['ValorTotal'] = df_table['ValorTotal'].apply(lambda x: f"R$ {x:,.2f}")

st.dataframe(
    df_table, 
    use_container_width=True, 
    height=400,
    hide_index=True
)

st.caption("Dashboard Comercial | v.Final")
