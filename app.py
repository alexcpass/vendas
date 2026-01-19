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

    /* --- BLOCO DE DESTAQUE (GRADIENTE AZUL/ROXO) --- */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) {
        background: linear-gradient(135deg, #4169E1 0%, #7B68EE 100%);
        border-radius: 16px;
        padding: 25px !important;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(65, 105, 225, 0.25);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Textos dentro do Destaque */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) * {
        color: white !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.8) !important;
    }

    /* BOTÕES */
    .stButton > button {
        width: 100%;
        padding-top: 8px;
        padding-bottom: 8px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Botões Inativos (Glass Effect no Destaque) */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) .stButton > button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.15);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div#highlight_marker) .stButton > button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.3);
    }
    
    /* Ajustes Gerais */
    h1 { margin: 0; padding: 0; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. FUNÇÃO DE PROCESSAMENTO (ETL)
# -----------------------------------------------------------------------------
@st.cache_data
def process_data(v_file, c_file, p_file):
    try:
        # Carregamento
        vendas = pd.read_csv(v_file)
        clientes = pd.read_csv(c_file)
        produtos = pd.read_csv(p_file)

        # Validação básica
        if 'ClienteID' not in vendas.columns or 'ProdutoID' not in vendas.columns:
            return None, "O arquivo de Vendas deve conter as colunas 'ClienteID' e 'ProdutoID'."

        # Merges
        df = vendas.merge(clientes, on='ClienteID', how='left').merge(produtos, on='ProdutoID', how='left')
        
        # Conversão de Moeda (Remove ponto milhar, troca virgula por ponto)
        if df['ValorTotal'].dtype == 'object':
            df['ValorTotal'] = (
                df['ValorTotal'].astype(str)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .astype(float)
            )
        
        # Datas
        df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
        df['Ano'] = df['DataVenda'].dt.year
        df['Mes'] = df['DataVenda'].dt.month
        
        meses_map = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
                     7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
        df['MesNome'] = df['Mes'].map(meses_map)
        
        return df, None
    except Exception as e:
        return None, str(e)

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

# Tela de Bloqueio (Espera Upload)
if not all([v_file, c_file, p_file]):
    st.markdown("""
        <div style='text-align: center; padding: 80px;'>
            <h1 style='color: #cbd5e0;'>Aguardando Arquivos...</h1>
            <p style='color: #718096;'>Por favor, faça o upload de Vendas, Clientes e Produtos na barra lateral.</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# Executa processamento
df, erro = process_data(v_file, c_file, p_file)

if erro:
    st.error(f"Erro no processamento: {erro}")
    st.stop()

# -----------------------------------------------------------------------------
# 4. ÁREA DE DESTAQUE (GRADIENTE) - FILTRO ANO E KPIs
# -----------------------------------------------------------------------------
with st.container():
    # Marcador invisível para aplicar o CSS de gradiente
    st.markdown('<div id="highlight_marker"></div>', unsafe_allow_html=True)
    
    st.markdown("### 📅 Período de Análise & Resultados")
    
    # Filtro de Ano
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

    # Filtragem Lógica para KPIs
    df_filtered = df.copy()
    if st.session_state.ano != "Todos":
        df_filtered = df_filtered[df_filtered['Ano'] == st.session_state.ano]

    # KPIs
    faturamento = df_filtered['ValorTotal'].sum()
    qtd_vendas = df_filtered['VendaID'].nunique()
    ticket = faturamento / qtd_vendas if qtd_vendas > 0 else 0
    clientes_unicos = df_filtered['ClienteID'].nunique()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Faturamento Total", f"R$ {faturamento:,.0f}")
    k2.metric("📦 Volume de Vendas", f"{qtd_vendas}")
    k3.metric("🎯 Ticket Médio", f"R$ {ticket:,.0f}")
    k4.metric("👥 Clientes Ativos", f"{clientes_unicos}")

# -----------------------------------------------------------------------------
# 5. FILTROS DA SIDEBAR (SECUNDÁRIOS)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    cat_opts = ['Todas'] + sorted(df['Categoria'].dropna().unique().tolist())
    cat_sel = st.selectbox("Categoria", cat_opts)
    
    pag_opts = ['Todas'] + sorted(df['FormaPagamento'].dropna().unique().tolist())
    pag_sel = st.selectbox("Forma de Pagamento", pag_opts)

# Aplicação dos Filtros Secundários
if cat_sel != 'Todas': 
    df_filtered = df_filtered[df_filtered['Categoria'] == cat_sel]
if pag_sel != 'Todas': 
    df_filtered = df_filtered[df_filtered['FormaPagamento'] == pag_sel]

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. GRÁFICOS
# -----------------------------------------------------------------------------

# GRÁFICO 1: FATURAMENTO (Light Theme)
st.markdown("### 📈 Evolução do Faturamento")
df_fat = df_filtered.groupby(['Mes', 'MesNome'])['ValorTotal'].sum().reset_index().sort_values('Mes')

fig_fat = px.bar(
    df_fat, 
    x='MesNome', 
    y='ValorTotal', 
    text='ValorTotal', 
    color_discrete_sequence=['#4169E1']
)
fig_fat.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
fig_fat.update_layout(height=350, plot_bgcolor='white', margin=dict(t=20))
st.plotly_chart(fig_fat, use_container_width=True)

# GRÁFICO 2: VOLUME DE VENDAS (Dark Theme & Laranja Suave)
# Este é o gráfico corrigido para evitar o ValueError e NameError
st.markdown("### 📊 Sazonalidade de Vendas")
df_vol = df_filtered.groupby(['Mes', 'MesNome'])['VendaID'].count().reset_index().sort_values('Mes')

fig_vol = go.Figure()

# Camada 1: Barras (Cor Laranja Suave)
fig_vol.add_trace(go.Bar(
    x=df_vol['MesNome'], 
    y=df_vol['VendaID'],
    name='Volume',
    marker_color='#F6AD55',  # Laranja Suave
    opacity=0.9,
    text=df_vol['VendaID'],
    textposition='inside',
    textfont=dict(color='black', size=14) # Removido 'weight' para evitar erro
))

# Camada 2: Linha (Roxo Claro para contraste)
fig_vol.add_trace(go.Scatter(
    x=df_vol['MesNome'], 
    y=df_vol['VendaID'],
    mode='lines+markers', 
    name='Tendência',
    line=dict(color='#9F7AEA', width=4), 
    marker=dict(size=10, color='#9F7AEA', line=dict(color='white', width=2))
))

fig_vol.update_layout(
    height=400,
    # Fundo Escuro Perolado
    plot_bgcolor='#4A5568', 
    paper_bgcolor='#2D3748',
    font=dict(color='white'), # Define texto global como branco
    xaxis=dict(
        showgrid=False, 
        tickfont=dict(color='white', size=13), # Removido 'weight'
        linecolor='#A0AEC0'
    ),
    yaxis=dict(
        showgrid=True, 
        gridcolor='#718096', 
        title=dict(text='Quantidade'), # Sintaxe segura
        tickfont=dict(color='white')
    ),
    legend=dict(
        orientation="h", 
        y=1.1, x=0,
        font=dict(color='white'),
        bgcolor='rgba(0,0,0,0)'
    ),
    margin=dict(l=20, r=20, t=50, b=20)
)
st.plotly_chart(fig_vol, use_container_width=True)

# GRÁFICO 3: TOP 10 PRODUTOS (Light Theme)
st.markdown("### 🏆 Top 10 Produtos")
df_top = df_filtered.groupby('NomeProduto')['ValorTotal'].sum().reset_index().sort_values('ValorTotal').tail(10)

fig_prod = px.bar(
    df_top, 
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
    textfont=dict(color='#d32f2f') # Removido 'weight'
)
fig_prod.update_layout(
    height=450, 
    plot_bgcolor='white', 
    xaxis=dict(showgrid=True, gridcolor='#f1f5f9'), 
    coloraxis_showscale=False
)
st.plotly_chart(fig_prod, use_container_width=True)

# TABELA FINAL
st.markdown("---")
st.markdown("### 📋 Registro Detalhado")
df_table = df_filtered[['DataVenda', 'NomeCliente', 'NomeProduto', 'Quantidade', 'ValorTotal', 'FormaPagamento']].sort_values('DataVenda', ascending=False).head(50)
df_table['DataVenda'] = df_table['DataVenda'].dt.strftime('%d/%m/%Y')
df_table['ValorTotal'] = df_table['ValorTotal'].apply(lambda x: f"R$ {x:,.2f}")

st.dataframe(df_table, use_container_width=True, height=400, hide_index=True)

st.caption("Dashboard Comercial | v.DarkPearl")
