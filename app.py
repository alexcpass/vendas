import streamlit as st
import pandas as pd
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
    
    /* BOTÕES DE ANO */
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
        
        # Tratamento de Valor Monetário
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
        
        # Nomes dos meses
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

# Tela de bloqueio
if not all([v_file, c_file, p_file]):
    st.markdown("""
        <div style='text-align: center; padding: 80px;'>
            <h1 style='color: #cbd5e0;'>Aguardando Arquivos...</h1>
            <p style='color: #718096;'>Por favor, faça o upload de Vendas, Clientes e Produtos na barra lateral.</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

df = process_data(v_file, c_file, p_file)

# -----------------------------------------------------------------------------
# 4. ÁREA DE DESTAQUE (GRADIENTE) - FILTROS E KPIs
# -----------------------------------------------------------------------------

# Cria um container principal para o Cabeçalho + Filtros + KPIs
with st.container():
    # MARCADOR INVISÍVEL PARA O CSS ALVO
    st.markdown('<div id="highlight_marker"></div>', unsafe_allow_html=True)
    
    # Cabeçalho da Seção
    st.markdown("### 📅 Período de Análise & Resultados")
    st.markdown("Selecione o ano para filtrar a performance comercial.")

    # --- FILTRO DE ANO ---
    anos = sorted(df['Ano'].unique())
    if 'ano' not in st.session_state: st.session_state.ano = anos[-1]

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
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- APLICAÇÃO DOS FILTROS (LOGICA) ---
    cat_sel = 'Todas'
    pag_sel = 'Todas'
    
    df_filtered = df.copy()
    if st.session_state.ano != "Todos":
        df_filtered = df_filtered[df_filtered['Ano'] == st.session_state.ano]

    # --- KPIs ---
    faturamento = df_filtered['ValorTotal'].sum()
    qtd_vendas = df_filtered['VendaID'].nunique()
    ticket_medio = faturamento / qtd_vendas if qtd_vendas > 0 else 0
    clientes_unicos = df_filtered['ClienteID'].nunique()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Faturamento Total", f"R$ {faturamento:,.0f}")
    k2.metric("📦 Volume de Vendas", f"{qtd_vendas}")
    k3.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.0f}")
    k4.metric("👥 Clientes Ativos", f"{clientes_unicos}")

# -----------------------------------------------------------------------------
# 5. RESTANTE DOS FILTROS (SIDEBAR)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 Filtros Detalhados")
    cat_opts = ['Todas'] + sorted(df['Categoria'].dropna().unique().tolist())
    cat_sel = st.selectbox("Categoria", cat_opts)
    
    pag_opts = ['Todas'] + sorted(df['FormaPagamento'].dropna().unique().tolist())
    pag_sel = st.selectbox("Forma de Pagamento", pag_opts)

if cat_sel != 'Todas':
    df_filtered = df_filtered[df_filtered['Categoria'] == cat_sel]
if pag_sel != 'Todas':
    df_filtered = df_filtered[df_filtered['FormaPagamento'] == pag_sel]

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. GRÁFICOS
# -----------------------------------------------------------------------------

# GRÁFICO 2: VOLUME DE VENDAS (MISTO: BARRAS LARANJA SUAVE + LINHAS + FUNDO ESCURO PEROLADO)
st.markdown("### 📊 Sazonalidade de Vendas")
df_vol_mensal = df_filtered.groupby(['Mes', 'MesNome'])['VendaID'].count().reset_index().sort_values('Mes')

fig_vol = go.Figure()
# Barras (Laranja Suave)
fig_vol.add_trace(go.Bar(
    x=df_vol_mensal['MesNome'], y=df_vol_mensal['VendaID'],
    name='Volume',
    marker_color='#F6AD55', # Laranja Suave
    opacity=0.8
))
# Linha (Destaque)
fig_vol.add_trace(go.Scatter(
    x=df_vol_mensal['MesNome'], y=df_vol_mensal['VendaID'],
    mode='lines+markers+text', name='Tendência',
    line=dict(color='#7B68EE', width=4), # Medium Slate Blue
    marker=dict(size=10, color='#7B68EE', line=dict(color='white', width=2)),
    text=df_vol_mensal['VendaID'], textposition='top center',
    textfont=dict(size=14, color='black', weight='bold')
))
fig_vol.update_layout(
    height=400,
    plot_bgcolor='#4A5568',      # Fundo Escuro Perolado
    paper_bgcolor='#2D3748',      # Fundo do Papel Escuro
    xaxis=dict(
        showgrid=False,
        tickfont=dict(color='white', size=12, weight='bold'), # Meses em Branco
        linecolor='#A0AEC0'
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#718096', # Grid cinza claro
        title='Qtd. Vendas',
        titlefont=dict(color='white'),
        tickfont=dict(color='white')
    ),
    showlegend=True,
    legend=dict(
        orientation="h", y=1.1, x=0,
        font=dict(color='white')
    ),
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig_vol, use_container_width=True)

st.caption("Dashboard Comercial | v.Gradient")
