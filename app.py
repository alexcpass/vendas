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
    /* IMPORTS & GERAL */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .main { background-color: #f5f7fa; font-family: 'Inter', sans-serif; }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1f36, #0f1419); }
    section[data-testid="stSidebar"] * { color: white !important; }

    /* --- ESTILO DO BLOCO DE DESTAQUE (GRADIENTE) --- */
    /* Usamos um truque de CSS (:has) para estilizar o container que tem o ID específico */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) {
        background: linear-gradient(135deg, #4169E1 0%, #7B68EE 100%); /* Royal Blue -> Medium Slate Blue */
        border-radius: 16px;
        padding: 25px !important;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(65, 105, 225, 0.25);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Textos dentro do bloco de destaque */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) h1,
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) h2,
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) h3,
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) p,
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) span,
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) div[data-testid="stMarkdownContainer"] p {
        color: white !important;
    }

    /* Métricas dentro do bloco de destaque */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 14px;
        font-weight: 500;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 32px;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* BOTÕES DENTRO DO DESTAQUE */
    /* Botão Padrão (Inativo) no fundo escuro */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) .stButton > button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.15);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) .stButton > button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.3);
        border-color: white;
    }
    
    /* Botão Ativo no fundo escuro */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) .stButton > button[kind="primary"] {
        background-color: white;
        color: #4169E1; /* Texto azul para contraste */
        border: none;
        font-weight: 800;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* Layout dos Botões (Largura total e altura reduzida) */
    .stButton > button {
        width: 100%;
        padding-top: 8px;
        padding-bottom: 8px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    /* Ajustes Gerais */
    h1 { margin: 0; padding: 0; }
    .block-container { padding-top: 2rem; }
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
    # MARCADOR INVISÍVEL PARA O CSS ALVO (IMPORTANTE)
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
    # (Filtros laterais continuam existindo mas aplicamos a lógica aqui para calcular os KPIs)
    cat_sel = 'Todas'
    pag_sel = 'Todas'
    
    # Verificação rápida se o usuário mexeu na sidebar (para manter consistência)
    # Se quiser mover os filtros da sidebar para cá, basta descomentar e adaptar.
    
    df_filtered = df.copy()
    if st.session_state.ano != "Todos":
        df_filtered = df_filtered[df_filtered['Ano'] == st.session_state.ano]

    # --- KPIs ---
    faturamento = df_filtered['ValorTotal'].sum()
    qtd_vendas = df_filtered['VendaID'].nunique()
    ticket_medio = faturamento / qtd_vendas if qtd_vendas > 0 else 0
    clientes_unicos = df_filtered['ClienteID'].nunique()

    # Layout de Colunas dos KPIs
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

# Reaplica filtros secundários
if cat_sel != 'Todas':
    df_filtered = df_filtered[df_filtered['Categoria'] == cat_sel]
if pag_sel != 'Todas':
    df_filtered = df_filtered[df_filtered['FormaPagamento'] == pag_sel]

# Recalcula KPIs visuais apenas para os gráficos abaixo (Os KPIs do topo são globais do ano)
# Se quiser que os KPIs do topo obedeçam aos filtros da sidebar, mova a lógica de cálculo para depois deste bloco.

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. GRÁFICOS
# -----------------------------------------------------------------------------

# GRÁFICO 1: FATURAMENTO MENSAL
st.markdown("### 📈 Evolução do Faturamento")
df_fat_mensal = df_filtered.groupby(['Mes', 'MesNome'])['ValorTotal'].sum().reset_index().sort_values('Mes')

fig_fat = px.bar(
    df_fat_mensal, 
    x='MesNome', 
    y='ValorTotal', 
    text='ValorTotal',
    color_discrete_sequence=['#4169E1'] # Royal Blue para combinar
)
fig_fat.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
fig_fat.update_layout(height=350, plot_bgcolor='white', margin=dict(t=30, b=0, l=0, r=0))
st.plotly_chart(fig_fat, use_container_width=True)

# GRÁFICO 2: VOLUME DE VENDAS
st.markdown("### 📊 Sazonalidade de Vendas")
df_vol_mensal = df_filtered.groupby(['Mes', 'MesNome'])['VendaID'].count().reset_index().sort_values('Mes')

fig_vol = go.Figure()
# Barras (Fundo suave)
fig_vol.add_trace(go.Bar(
    x=df_vol_mensal['MesNome'], y=df_vol_mensal['VendaID'],
    name='Volume', marker_color='#E6E6FA', opacity=0.8 # Lavanda suave
))
# Linha (Destaque)
fig_vol.add_trace(go.Scatter(
    x=df_vol_mensal['MesNome'], y=df_vol_mensal['VendaID'],
    mode='lines+markers+text', name='Tendência',
    line=dict(color='#7B68EE', width=4), # Medium Slate Blue
    marker=dict(size=10, color='#7B68EE', line=dict(color='white', width=2)),
    text=df_vol_mensal['VendaID'], textposition='top center',
    textfont=dict(size=14, color='#1a1f36', weight='bold')
))
fig_vol.update_layout(
    height=400, plot_bgcolor='#f8f9fa', paper_bgcolor='white',
    xaxis=dict(showgrid=False, tickfont=dict(color='black', weight='bold')),
    yaxis=dict(showgrid=True, gridcolor='#e0e0e0'),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", y=1.1, x=0)
)
st.plotly_chart(fig_vol, use_container_width=True)

# GRÁFICO 3: TOP 10 PRODUTOS
st.markdown("### 🏆 Top 10 Produtos")
df_top_prod = df_filtered.groupby('NomeProduto')['ValorTotal'].sum().reset_index()
df_top_prod = df_top_prod.sort_values('ValorTotal', ascending=True).tail(10)

fig_prod = px.bar(
    df_top_prod, y='NomeProduto', x='ValorTotal', 
    orientation='h', text='ValorTotal',
    color='ValorTotal', color_continuous_scale='Blues'
)
fig_prod.update_traces(
    texttemplate='R$ %{text:,.0f}', textposition='outside',
    textfont=dict(color='#d32f2f', weight='bold')
)
fig_prod.update_layout(
    height=450, plot_bgcolor='white', 
    xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
    coloraxis_showscale=False
)
st.plotly_chart(fig_prod, use_container_width=True)

# TABELA
st.markdown("---")
st.markdown("### 📋 Registro de Vendas")
df_table = df_filtered[['DataVenda', 'NomeCliente', 'NomeProduto', 'Quantidade', 'ValorTotal', 'FormaPagamento']].sort_values('DataVenda', ascending=False).head(50)
df_table['DataVenda'] = df_table['DataVenda'].dt.strftime('%d/%m/%Y')
df_table['ValorTotal'] = df_table['ValorTotal'].apply(lambda x: f"R$ {x:,.2f}")

st.dataframe(df_table, use_container_width=True, height=400, hide_index=True)
st.caption("Dashboard Comercial | v.Gradient")
