import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E CSS (ESTILO TEAL/MINT)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Dashboard Analítico", page_icon="📊", layout="wide")

st.markdown("""
<style>
    /* Importando fonte limpa */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    /* GERAL */
    .stApp {
        background-color: #F2F4F8; /* Fundo cinza claro igual da imagem */
        font-family: 'Roboto', sans-serif;
    }

    /* SIDEBAR (Barra lateral estilo "Menu Verde") */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #26A69A 0%, #00897B 100%); /* Gradiente Teal */
        color: white;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }

    /* CARDS (Cartões Brancos Arredondados) */
    .dashboard-card {
        background-color: white;
        border-radius: 15px; /* Arredondamento forte */
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* ESTILO DOS KPIS (Topo) */
    .kpi-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .kpi-icon {
        font-size: 24px;
        margin-bottom: 10px;
        background: #E0F2F1; /* Fundo icone bem claro */
        color: #00897B;
        padding: 10px;
        border-radius: 50%;
    }
    .kpi-label {
        font-size: 14px;
        color: #757575;
        font-weight: 500;
        text-transform: uppercase;
    }
    .kpi-value {
        font-size: 22px;
        color: #333;
        font-weight: 700;
        margin-top: 5px;
    }

    /* TITULO DA SEÇÃO */
    .section-title {
        text-align: center;
        font-weight: 700;
        color: #37474F;
        margin-bottom: 20px;
        font-size: 18px;
        text-transform: uppercase;
    }

    /* AJUSTES NOS BOTÕES DO STREAMLIT PARA FICAR BRANCO/CLEAN */
    .stButton > button {
        background-color: rgba(255,255,255,0.2);
        color: white;
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 8px;
    }
    .stButton > button:hover {
        background-color: white;
        color: #00897B;
    }
    
    /* Remove padding excessivo do topo */
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. PROCESSAMENTO DE DADOS
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(v, c, p):
    try:
        vendas = pd.read_csv(v)
        clientes = pd.read_csv(c)
        produtos = pd.read_csv(p)
        
        df = vendas.merge(clientes, on='ClienteID', how='left').merge(produtos, on='ProdutoID', how='left')
        
        # Tratamentos
        df['ValorTotal'] = df['ValorTotal'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
        df['Ano'] = df['DataVenda'].dt.year
        df['Mes'] = df['DataVenda'].dt.month
        
        meses_map = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
        df['MesNome'] = df['Mes'].map(meses_map)
        
        return df
    except Exception:
        return None

# -----------------------------------------------------------------------------
# 3. SIDEBAR (Navegação Visual)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<div style='text-align: center; margin-bottom: 30px;'><h1 style='font-size: 40px;'>📊</h1></div>", unsafe_allow_html=True)
    
    st.markdown("### PAINEL DE CONTROLE")
    
    # Upload
    with st.expander("📂 Carregar Dados", expanded=True):
        v_file = st.file_uploader("Vendas", type=['csv'])
        c_file = st.file_uploader("Clientes", type=['csv'])
        p_file = st.file_uploader("Produtos", type=['csv'])
    
    st.markdown("---")
    
    # Filtros
    st.markdown("### FILTROS")
    
    # Placeholder para filtros dinâmicos
    filtros_placeholder = st.container()

if not all([v_file, c_file, p_file]):
    st.markdown("""
        <div style='text-align:center; margin-top: 50px; color: #546E7A;'>
            <h2>Aguardando Dados...</h2>
            <p>Faça o upload dos arquivos CSV na barra lateral (verde).</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

df = load_data(v_file, c_file, p_file)

# --- LÓGICA DE FILTROS NA SIDEBAR ---
with filtros_placeholder:
    anos = sorted(df['Ano'].unique())
    if 'ano' not in st.session_state: st.session_state.ano = anos[-1]
    
    # Seletor de Ano
    st.write("Período (Ano):")
    col_a1, col_a2 = st.columns(2)
    if col_a1.button("Todos", key="btn_all"): st.session_state.ano = "Todos"
    if col_a2.button(str(anos[-1]), key=f"btn_{anos[-1]}"): st.session_state.ano = anos[-1]
    
    # Selectboxes estilizados
    cat = st.selectbox("Departamento / Categoria", ['Todos'] + sorted(df['Categoria'].unique().tolist()))
    pay = st.selectbox("Forma Pagamento", ['Todos'] + sorted(df['FormaPagamento'].unique().tolist()))

# Aplicar filtros
df_f = df.copy()
if st.session_state.ano != "Todos": df_f = df_f[df_f['Ano'] == st.session_state.ano]
if cat != 'Todos': df_f = df_f[df_f['Categoria'] == cat]
if pay != 'Todos': df_f = df_f[df_f['FormaPagamento'] == pay]

# -----------------------------------------------------------------------------
# 4. CORPO DO DASHBOARD (ESTILO IMAGEM)
# -----------------------------------------------------------------------------

# Cabeçalho Centralizado
st.markdown(f"<div class='section-title'>ANÁLISE GERAL - PERFORMANCE COMERCIAL {st.session_state.ano}</div>", unsafe_allow_html=True)

# --- LINHA 1: KPIS (Cards Brancos com Ícones) ---
k1, k2, k3, k4 = st.columns(4)

fat = df_f['ValorTotal'].sum()
qtd = df_f['VendaID'].nunique()
tkt = fat/qtd if qtd > 0 else 0
cli = df_f['ClienteID'].nunique()

def render_kpi(col, icon, label, value):
    col.markdown(f"""
    <div class="dashboard-card kpi-container">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

render_kpi(k1, "💰", "Faturamento Total", f"R$ {fat:,.0f}")
render_kpi(k2, "📦", "Volume de Vendas", f"{qtd}")
render_kpi(k3, "📈", "Ticket Médio", f"R$ {tkt:,.0f}")
render_kpi(k4, "👥", "Clientes Ativos", f"{cli}")

# --- LINHA 2: GRÁFICO PRINCIPAL (Largo, estilo da imagem) ---
st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
st.markdown("**Evolução Mensal (Vendas vs Faturamento)**")

# Dados
mensal = df_f.groupby(['Mes','MesNome']).agg({'ValorTotal':'sum', 'VendaID':'count'}).reset_index().sort_values('Mes')

# Gráfico Combo (Barras + Linha) com cores Teal
fig = go.Figure()

# Barras (Faturamento)
fig.add_trace(go.Bar(
    x=mensal['MesNome'], 
    y=mensal['ValorTotal'],
    name='Faturamento',
    marker_color='#4DB6AC', # Teal Claro
    text=mensal['ValorTotal'],
    texttemplate='R$ %{text:.2s}',
    textposition='auto'
))

# Linha (Tendência)
fig.add_trace(go.Scatter(
    x=mensal['MesNome'],
    y=mensal['ValorTotal'],
    mode='lines+markers',
    name='Tendência',
    line=dict(color='#00695C', width=3), # Teal Escuro
    marker=dict(size=8, color='white', line=dict(color='#00695C', width=2))
))

fig.update_layout(
    height=350,
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis=dict(showgrid=False, linecolor='#eee'),
    yaxis=dict(showgrid=True, gridcolor='#f5f5f5', showline=False, showticklabels=False), # Limpo como na imagem
    legend=dict(orientation="h", y=1.1, x=1)
)

st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- LINHA 3: GRÁFICOS SECUNDÁRIOS (Lado a Lado) ---
c_left, c_right = st.columns(2)

with c_left:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("**Top Produtos (Receita)**")
    
    top_prod = df_f.groupby('NomeProduto')['ValorTotal'].sum().reset_index().sort_values('ValorTotal', ascending=True).tail(8)
    
    fig2 = px.bar(
        top_prod, 
        y='NomeProduto', 
        x='ValorTotal', 
        orientation='h',
        text='ValorTotal',
        color_discrete_sequence=['#26A69A'] # Teal Padrão
    )
    fig2.update_traces(texttemplate='R$ %{text:.2s}', textposition='inside')
    fig2.update_layout(
        height=300,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=10,l=0,r=0,b=0),
        xaxis=dict(showgrid=True, gridcolor='#f5f5f5'),
        yaxis=dict(title=None)
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c_right:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("**Mix de Formas de Pagamento**")
    
    pagamento = df_f.groupby('FormaPagamento')['ValorTotal'].sum().reset_index()
    
    # Donut Chart limpo
    fig3 = px.pie(
        pagamento, 
        values='ValorTotal', 
        names='FormaPagamento', 
        hole=0.6,
        color_discrete_sequence=['#004D40', '#00695C', '#00897B', '#26A69A', '#4DB6AC', '#80CBC4'] # Paleta Teal completa
    )
    fig3.update_traces(textinfo='percent+label', textposition='outside')
    fig3.update_layout(
        height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=False
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- TABELA DE DADOS (Rodapé) ---
st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
st.markdown("**Detalhamento de Transações**")
df_show = df_f[['DataVenda', 'NomeCliente', 'NomeProduto', 'ValorTotal', 'FormaPagamento']].sort_values('DataVenda', ascending=False).head(50)
df_show['DataVenda'] = df_show['DataVenda'].dt.strftime('%d/%m/%Y')
df_show['ValorTotal'] = df_show['ValorTotal'].apply(lambda x: f"R$ {x:,.2f}")

st.dataframe(df_show, use_container_width=True, height=300, hide_index=True)
st.markdown("</div>", unsafe_allow_html=True)
